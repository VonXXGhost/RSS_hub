from django.db import models
import django.utils.timezone as timezone


class UpdatedHashTable(models.Model):

    name = models.CharField(max_length=255, primary_key=True)
    hash = models.CharField(max_length=255, null=True)


class BaseItem(models.Model):

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    pub_date = models.DateTimeField('pub date', default=timezone.now)


class AnitamaArticleItem(BaseItem):

    ARTICLE_URL_TEMPLATE = 'http://www.anitama.cn/article/{0}'

    aid = models.CharField(max_length=255, primary_key=True)
    author = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    channel = models.CharField(max_length=255)
    cover = models.URLField()
    content = models.TextField(null=True)

    @property
    def link(self):
        return self.ARTICLE_URL_TEMPLATE.format(self.aid)

    def get_absolute_url(self):
        return self.link