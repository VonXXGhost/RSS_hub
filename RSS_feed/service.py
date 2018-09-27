import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
import lxml
import logging
import hashlib

from .models import *
from django.urls import reverse
from django.conf import settings
from django_push.publisher import ping_hub
from .feeds import *


logger = logging.getLogger('RSS_feed.service')


def publish(feed_type):
    try:
        ping_hub('http://%s/%s' % (settings.SITE_DOMAIN, feed_type.link))
        logger.info('published succeeded.')
    except Exception as e:
        logger.error('published failed.')
        logger.error(e)


class AnitamaArticleFeedService():

    API_URL = 'https://app.anitama.net/timeline'
    ARTICLE_INFO_API_TEMPLATE = 'https://app.anitama.net/article/{0}'
    CHANNEL_URL = 'http://www.anitama.cn/channel'
    CHECK_HASH_NAME = 'AnitamaLatestArticle'
    logger = logging.getLogger('RSS_feed.service.AnitamaArticleFeedService')

    def _save_article(self, article_info: dict) -> bool:
        article, created = AnitamaArticleItem.objects.get_or_create(
            aid=article_info['aid'],
            defaults={
                'title': article_info['title'],
                'subtitle': article_info['subtitle'],
                'author': article_info['author'],
                'description': article_info['intro'],
                'pub_date': article_info['releaseDate'],
                'cover': article_info['cover']['url'],
                'channel': article_info['channel'],
                'content': article_info['content'],
            }
        )
        if created:
            return True
        self.logger.info('<{0}>[{1}] saved.'.format(article_info['title'], article_info['aid']))
        return False

    def _get_channel_of_articles_from_html(self, aids: List[str]) -> Dict[str, str]:
        self.logger.debug('getting channel results')
        response = requests.get(self.CHANNEL_URL)
        soup = BeautifulSoup(response.text, 'lxml')
        result = {}
        for aid in aids:
            if not aid:
                continue
            item = soup.find('a', href=re.compile(aid), class_='item')
            if item:
                channel = ''.join(item.find(class_='channel').strings)
                result[aid] = str(channel)
            else:
                self.logger.error('can\'t find channel of ' + aid)
                result[aid] = ''
        self.logger.debug('get channel results: ' + str(result))
        return result

    def _get_channel_content_of_article(self, aid: str) -> Dict[str, str]:
        response = requests.get(self.ARTICLE_INFO_API_TEMPLATE.format(aid))
        try:
            j = response.json()
            channel = j['data']['article']['channel']['channelName']
            content = j['data']['article']['html']
        except KeyError:
            channel = None
            content = None
        return {'channel': channel, 'content': content}

    def _get_channel_content_of_articles(self, aids: List[str]) -> Dict[str, Dict[str, str]]:
        res = {}
        for aid in aids:
            res[aid] = self._get_channel_content_of_article(aid)
        self.logger.debug('get channel and content results: ' + str(res))
        return res

    def _check_if_updated(self, articles: List[dict]) -> bool:
        md5 = hashlib.new('md5', str(articles[0]).encode('utf-8')).hexdigest()
        if UpdatedHashTable.objects.filter(name=self.CHECK_HASH_NAME, hash=md5):
            self.logger.debug('no need to update')
            return False
        UpdatedHashTable.objects.update_or_create(
            name=self.CHECK_HASH_NAME,
            defaults={'hash': md5}
        )
        self.logger.info('need to update')
        return True

    def update_timeline(self):
        self.logger.info('timeline updating')
        response = requests.get(self.API_URL)
        articles = [a for a in response.json()['data']['page']['list'] if 'aid' in a]
        if not self._check_if_updated(articles):
            return
        aids = [a['aid'] for a in articles]
        channels_contents = self._get_channel_content_of_articles(aids)
        for article_info in articles:
            article_info['channel'] = channels_contents[article_info['aid']]['channel']
            article_info['content'] = channels_contents[article_info['aid']]['content']
            if not self._save_article(article_info):
                break
        self.logger.info('timeline updated')
        publish(AnitamaTimelineFeed)
