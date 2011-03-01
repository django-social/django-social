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
def file_edit(request, library, id=None, file_id=None):

    def image_file(name, description):
        file = form.fields['file']
        file = file.save('library_image', settings.LIBRARY_IMAGE_SIZES, LIBRARY_IMAGE_RESIZE_TASK)
        file.name = name
        file.description = description
        file.save()
        return file


    def video_file(name, description):
        file = form.fields['file']
        file = file.save('library_video', settings.LIBRARY_VIDEO_SIZES, LIBRARY_VIDEO_RESIZE_TASK)
        file.name = name
        file.description = description
        file.save()
        return file

    def audio_file(name, description):
        buffer = StringIO()
        for chunk in request.FILES['file'].chunks():
            buffer.write(chunk)

        buffer.reset()

        file = File(type='library_audio')
        file.file.put(buffer, content_type='audio/mpeg')
        file.transformation = 'main.mp3'
        file.name = name
        file.description = description
        return file.save()

    params = {
        LIBRARY_TYPE_IMAGE: dict(
            file=image_file,
            successfully=_('Image successfully saved') if file_id else _('Image successfully added'),
            title=_('Editing image') if file_id else _('Adding image'),
            form=ImageAddForm,
        ),

        LIBRARY_TYPE_VIDEO: dict(
            file=video_file,
            successfully=_('Video successfully saved') if file_id else _('Video successfully added'),
            title=_('Editing video') if file_id else _('Adding video'),
            form=VideoAddForm,
        ),

        LIBRARY_TYPE_AUDIO: dict(
            file=audio_file,
            successfully=_('Audio successfully saved') if file_id else _('Audio successfully added'),
            title=_('Editing audio') if file_id else _('Adding audio'),
            form=AudioAddForm,
        ),
    }

    current_params = params[library]

    tree = get_library(library)

    if file_id:
        file = get_document_or_404(File, id=file_id)
        data = file._data
        node = tree.get(file.id)
        if node.ancestors:
            current_folder = node.ancestors[-1]
            id = current_folder.id
        else:
            current_folder = None
    else:
        file = None
        data = {}
        if id:
            folder = get_document_or_404(Folder, id=id)
            current_folder = tree.get(folder.id)
            if not current_folder:
                raise Http404()
        else:
            current_folder = None

    if request.POST:
        form = current_params['form'](request.POST, request.FILES, initial=data)
        if file_id:
            form.fields['file'].required = False
        if form.is_valid():
            if 'file' in request.FILES:
                newfile = current_params['file'](form.cleaned_data['name'], form.cleaned_data['description'])

                if file_id:
                    tree.remove(file)
                    file.full_delete()

                if id:
                    tree.add(newfile, current_folder)
                else:
                    tree.add(newfile)
            else:
                # is file_id
                tree.rename(file, form.cleaned_data['name'])
            tree.save()
            messages.add_message(request, messages.SUCCESS, current_params['successfully'])
            return redirect_by_id('media_library:%s_index' % library, id)
    else:
        form = current_params['form'](initial=data)
    return direct_to_template(request,
                              'media_library/file_edit.html',
                              dict( title=current_params['title'],
                                    breadcrumb='media_library/_%s_breadcrumb.html' % library,
                                    form=form,
                                    current_folder=current_folder,
                                    file=file ) )