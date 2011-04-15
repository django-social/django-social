# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.file_library.views',
    url(r'^$', 'index', name='index'),
    url(r'^category/(?P<id>[a-f0-9]{24})/$', 'category_view', name='category_view'),

    url(r'^add/$', 'add_file', name='add_file'),

    url(r'^(?P<id>[a-f0-9]{24})/$', 'file_view', name='file_view'),
    url(r'^(?P<id>[a-f0-9]{24})/delete/$', 'file_delete', name='file_delete'),
    url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'file_edit', name='file_edit'),

    url(r'^category/add/$', 'add_category', name='add_category'),
)