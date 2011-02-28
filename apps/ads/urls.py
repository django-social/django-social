# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from django.conf import settings

urlpatterns = patterns('apps.ads.views',
    url(r'^$', 'list', name='list'),
    url(r'^add/$', 'add', name='add'),
    url(r'^(?P<id>[a-f0-9]{24})/$', 'view', name='view'),
    url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'edit', name='edit'),
    
    url(r'^get_cities/$', 'ajax_get_cities', name='get_cities'),
    url(r'^get_categories/$', 'ajax_get_categories', name='get_categories'),

)