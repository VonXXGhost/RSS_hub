from django_push.publisher.feeds import Feed
from .models import *
import logging
import datetime

logger = logging.getLogger('RSS_feed.feed')


class AnitamaTimelineFeed(Feed):
    title = 'Anitama'
    link = '/feed/anitama'
    description = 'Anitama timeline'
    channel_filter = ('News',)

    def items(self):
        return AnitamaArticleItem.objects.exclude(channel__in=self.channel_filter) \
                                        .order_by('-pub_date')[:10]

    def item_title(self, item):
        return item.title + ' - ' + item.subtitle

    def item_description(self, item):
        return item.content if item.content else item.description

    def item_author_name(self, item):
        return item.author

    def item_enclosure_url(self, item):
        return item.cover

    item_enclosure_length = 0

    item_enclosure_mime_type = "image/jpeg"

    def item_pubdate(self, item):
        return item.pub_date

    def item_categories(self, item):
        return (item.channel,)
