# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from .constants import LIBRARY_TYPE_AUDIO, LIBRARY_TYPE_IMAGE, LIBRARY_TYPE_VIDEO


urls = []
for library in [LIBRARY_TYPE_VIDEO, LIBRARY_TYPE_IMAGE, LIBRARY_TYPE_AUDIO]:
    params = { 'library': library }
    urls += [
    url(r'^%s/$' % library, 'index', name='%s_index' % library, kwargs=params),
    url(r'^%s/(?P<id>[a-f0-9]{24})/$' % library, 'index', name='%s_index' % library, kwargs=params),
    url(r'^%s/add/$' % library, '%s_add' % library, name='%s_add' % library),
    url(r'^%s/(?P<id>[a-f0-9]{24})/add/$' % library, '%s_add' % library, name='%s_add' % library),
    url(r'^%s/(?P<id>[a-f0-9]{24})/delete/$' % library, 'file_delete', name='%s_delete' % library, kwargs=params),

    url(r'^%s/folder/add/$' % library, 'folder_add', name='%s_folder_add' % library, kwargs=params),
    url(r'^%s/(?P<id>[a-f0-9]{24})/folder/add/$' % library, 'folder_add', name='%s_folder_add' % library, kwargs=params),
    url(r'^%s/folder/(?P<id>[a-f0-9]{24})/edit/$' % library, 'folder_edit', name='%s_folder_edit' % library, kwargs=params),
    url(r'^%s/(?P<id>[a-f0-9]{24})/folder/delete/$' % library, 'folder_delete', name='%s_folder_delete' % library, kwargs=params),
    ]

urlpatterns = patterns('apps.media_library.views', *urls )