# -*- coding: utf-8 -*-


from django.conf.urls.defaults import patterns, url

from django.conf import settings

urlpatterns = patterns('apps.applications.views',
   url(r'^$', 'list', name='list'),
   url(r'^add/$', 'add', name='add'),
   url(r'^(?P<id>[a-f0-9]{24})/$', 'view', name='view'),
   url(r'^(?P<id>[a-f0-9]{24})/delete/$', 'delete', name='delete'),
)