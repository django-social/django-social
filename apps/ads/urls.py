# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from django.conf import settings

urlpatterns = patterns('apps.ads.views',
   url(r'^$', 'list', name='list'),
   url(r'^get_cities/$', 'ajax_get_cities', name='get_cities'),
)