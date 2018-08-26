from django.urls import path
from .feeds import *

urlpatterns = [
    path('anitama/', AnitamaTimelineFeed())
]