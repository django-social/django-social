# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.views.generic.simple import direct_to_template
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from apps.utils.stringio import StringIO

from mongoengine.django.shortcuts import get_document_or_404

from apps.media.documents import File, Tree, Folder


from .forms import ImageAddForm, VideoAddForm, AudioAddForm, FolderEditForm

from .constants import *

def get_library(name):
    assert name in (LIBRARY_TYPE_IMAGE, LIBRARY_TYPE_AUDIO, LIBRARY_TYPE_VIDEO, )
    library, created = Tree.objects.get_or_create(name='common_%s_library' % name)
    return library


def redirect_by_id(url, id=None):
    return redirect(reverse(url, args=[id]) if id else url)


@permission_required('superuser')
def folder_add(request, library, id=None):
    tree = get_library(library)

    if id:
        folder = get_document_or_404(Folder, id=id)
        parent = tree.get(folder.id)
        if not parent:
            raise Http404()
        current_folder = parent
    else:
        current_folder = None

    if request.POST:
        form = FolderEditForm(request.POST)

        if form.is_valid():
            folder = Folder(name=form.cleaned_data['name'])
            folder.save()

            if id:
                tree.add(folder, parent)
            else:
                tree.add(folder)
            tree.save()
            messages.add_message(request, messages.SUCCESS, _('Folder successfully added'))
            return redirect_by_id('media_library:%s_index' % library, id)
    else:
        form = FolderEditForm()
    return direct_to_template(request,
                              'media_library/folder_edit.html',
                              dict( breadcrumb='media_library/_%s_breadcrumb.html' % library,
                                    form=form,
                                    current_folder=current_folder ) )


@permission_required('superuser')
def folder_edit(request, library, id):
    tree = get_library(library)

    folder = get_document_or_404(Folder, id=id)
    current_folder = tree.get(folder.id)
    if not current_folder:
        raise Http404()

    if request.POST:
        form = FolderEditForm(request.POST, initial=folder._data)

        if form.is_valid():
            tree.rename(folder, form.cleaned_data['name'])
            current_folder.name = folder.name
            tree.save()
            messages.add_message(request, messages.SUCCESS, _('Folder successfully saved'))
            return redirect_by_id('media_library:%s_index' % library, id)
    else:
        form = FolderEditForm(initial=folder._data)
    return direct_to_template(request,
                              'media_library/folder_edit.html',
                              dict( breadcrumb='media_library/_%s_breadcrumb.html' % library,
                                    form=form,
                                    current_folder=current_folder,
                                    is_edit=True ) )


@permission_required('superuser')
def folder_delete(request, library, id):
    tree = get_library(library)
    folder = get_document_or_404(Folder, id=id)
    node = tree.get(folder.id)
    if not node:
        raise Http404()
    nodes = tree.remove(node)
    tree.save()

    for node in nodes:
        node.full_delete()

    messages.add_message(request, messages.SUCCESS, _('Folder successfully removed'))
    url = 'media_library:%s_index' % library
    return redirect(url)


@permission_required('superuser')
def file_delete(request, library, id):
    tree = get_library(library)
    file = get_document_or_404(File, id=id)
    tree.remove(file)
    tree.save()
    file.full_delete()
    messages.add_message(request, messages.SUCCESS, REMOVE_MESSAGES[library])
    return redirect('media_library:%s_index' % library)


def index(request, library, id=None):
    tree = get_library(library)

    if id:
        folder = get_document_or_404(Folder, id=id)
        parent = tree.get(folder.id)
        if not parent:
            raise Http404()
        items = parent.get_children()
        current_folder = parent
    else:
        items = tree.get_children()
        current_folder = None

    folders, files = Tree.sort_by_name(items)

    return direct_to_template(request, 'media_library/%s_index.html' % library,
                              dict(can_manage=request.user.has_perm('superuser'),
                                   current_folder=current_folder,
                                   folders=folders,
                                   files=files,
                                   ))


@permission_required('superuser')
def image_add(request, id=None):
    tree = get_library(LIBRARY_TYPE_IMAGE)

    if id:
        folder = get_document_or_404(Folder, id=id)
        parent = tree.get(folder.id)
        if not parent:
            raise Http404()
        current_folder = parent
    else:
        current_folder = None

    if request.POST:
        form = ImageAddForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.fields['file'].save('library_image', settings.LIBRARY_IMAGE_SIZES, LIBRARY_IMAGE_RESIZE_TASK)

            file.name = form.cleaned_data['name']
            file.description = form.cleaned_data['description']
            file.save()

            if id:
                tree.add(file, parent)
            else:
                tree.add(file)
            tree.save()
            messages.add_message(request, messages.SUCCESS, _('Image successfully added'))
            return redirect_by_id('media_library:image_index', id)
    else:
        form = ImageAddForm()
    return direct_to_template(request, 'media_library/image_add.html', dict( form=form, current_folder=current_folder ) )


@permission_required('superuser')
def video_add(request, id=None):
    tree = get_library(LIBRARY_TYPE_VIDEO)

    if id:
        folder = get_document_or_404(Folder, id=id)
        parent = tree.get(folder.id)
        if not parent:
            raise Http404()
        current_folder = parent
    else:
        current_folder = None

    if request.POST:
        form = VideoAddForm(request.POST, request.FILES)
        if form.is_valid():


            file = form.fields['file'].save('library_video', settings.LIBRARY_VIDEO_SIZES,
                                            LIBRARY_VIDEO_RESIZE_TASK)

            file.name = form.cleaned_data['name']
            file.description = form.cleaned_data['description']
            file.save()

            if id:
                tree.add(file, parent)
            else:
                tree.add(file)
            tree.save()

            messages.add_message(request, messages.SUCCESS, _('Video successfully added'))
            return redirect_by_id('media_library:video_index', id)
    else:
        form = VideoAddForm()

    return direct_to_template(request, 'media_library/video_add.html', dict( form=form, current_folder=current_folder ) )


@permission_required('superuser')
def audio_add(request, id=None):
    tree = get_library(LIBRARY_TYPE_AUDIO)

    if id:
        folder = get_document_or_404(Folder, id=id)
        parent = tree.get(folder.id)
        if not parent:
            raise Http404()
        current_folder = parent
    else:
        current_folder = None

    if request.POST:
        form = AudioAddForm(request.POST, request.FILES)
        if form.is_valid():

            buffer = StringIO()
            for chunk in request.FILES['file'].chunks():
                buffer.write(chunk)

            buffer.reset()

            file = File(type='library_audio')
            file.file.put(buffer, content_type='audio/mpeg')
            file.transformation = 'main.mp3'
            file.name = form.cleaned_data['name']
            file.description = form.cleaned_data['description']
            file.save()

            if id:
                tree.add(file, parent)
            else:
                tree.add(file)
            tree.save()

            messages.add_message(request, messages.SUCCESS, _('Audio successfully added'))
            return redirect_by_id('media_library:audio_index', id)
    else:
        form = AudioAddForm()

    return direct_to_template(request, 'media_library/audio_add.html', dict( form=form, current_folder=current_folder ) )