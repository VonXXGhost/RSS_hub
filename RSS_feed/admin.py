from django.contrib import admin
from .models import *


@admin.register(UpdatedHashTable)
class UpdatedHashTableAdmin(admin.ModelAdmin):
    pass


@admin.register(AnitamaArticleItem)
class AnitamaArticleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'author', 'channel', 'pub_date', 'aid')
    list_filter = ['pub_date']
    ordering = ['-pub_date']