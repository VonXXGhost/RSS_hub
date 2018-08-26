from .service import *
from celery import shared_task
import logging


logger = logging.getLogger('RSS_feed.tasks')


@shared_task()
def anitama_timeline_task():
    AnitamaArticleFeedService().update_timeline()

