# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.notes.views',
    url(r'^$', 'note_list', name='note_list'),
    url(r'^list/(?P<id>[a-f0-9]{24})/$', 'note_list', name='note_list'),
    url(r'^add/$', 'note_edit', name='note_add'),

    url(r'^(?P<note_id>[a-f0-9]{24})/$', 'note_view', name='note_view'),
    url(r'^(?P<note_id>[a-f0-9]{24})/edit/$', 'note_edit', name='note_edit'),
    url(r'^(?P<note_id>[a-f0-9]{24})/delete/$', 'note_delete',
        name='note_delete'),

    url(r'^delete/$', 'multiple_delete', name='multiple_delete'),

    url(r'^comment/(?P<comment_id>[a-f0-9]{24})/delete/$', 'comment_delete', name='comment_delete'),

)