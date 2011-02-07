# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from apps.utils.paginator import paginate
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings

from mongoengine.django.shortcuts import get_document_or_404

from apps.media.documents import File, Tree, Folder


from .forms import ImageAddForm, VideoAddForm, FolderEditForm

from .constants import *

def get_library(name):
    assert name in (LIBRARY_TYPE_IMAGE, LIBRARY_TYPE_AUDIO, LIBRARY_TYPE_VIDEO, )
    library, created = Tree.objects.get_or_create(name='common_%s_library' % name)
    return library


def can_manage_library(user):
    return user.has_perm('superuser')


def redirect_by_id(url, id=None):
    return redirect(reverse(url, args=[id]) if id else url)


def folder_add(request, library, template, id):
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
            return
    else:
        form = FolderEditForm()
    return direct_to_template(request, template, dict( form=form, current_folder=current_folder ) )


def folder_delete(request, library, id):
    tree = get_library(library)
    folder = get_document_or_404(Folder, id=id)
    node = tree.get(folder.id)
    if not node:
        raise Http404()
    ids = tree.remove(node)
    tree.save()
    messages.add_message(request, messages.SUCCESS, _('Folder successfully removed'))
    return redirect('media_library:image_index')


def image_index(request, id=None):
    tree = get_library(LIBRARY_TYPE_IMAGE)
    
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

    objects = paginate(request,
                       items,
                       len(items),
                       settings.LIBRARY_IMAGES_PER_PAGE
                       )

    return direct_to_template(request, 'media_library/image_index.html',
                              dict(
                                      objects=objects,
                                      can_manage=can_manage_library(request.user),
                                      current_folder=current_folder,
                                   )
                              )


@user_passes_test(can_manage_library)
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


@user_passes_test(can_manage_library)
def image_folder_add(request, id=None):
    response = folder_add(request, LIBRARY_TYPE_IMAGE, 'media_library/image_folder_add.html', id)
    if response is None:
        return redirect_by_id('media_library:image_index', id)
    return response


@user_passes_test(can_manage_library)
def image_folder_delete(request, id):
    return folder_delete(request, LIBRARY_TYPE_IMAGE, id)


@user_passes_test(can_manage_library)
def image_delete(request, id):
    tree = get_library(LIBRARY_TYPE_IMAGE)
    image = get_document_or_404(File, id=id)
    ids = tree.remove(image)
    tree.save()
    messages.add_message(request, messages.SUCCESS, _('Image successfully removed'))
    return redirect('media_library:image_index')


def video_index(request, id=None):
    tree = get_library(LIBRARY_TYPE_VIDEO)

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

    objects = paginate(request,
                       items,
                       len(items),
                       settings.LIBRARY_VIDEO_PER_PAGE
                       )

    return direct_to_template(request, 'media_library/video_index.html',
                              dict(objects=objects,
                                   can_manage=can_manage_library(request.user),
                                   current_folder=current_folder,
                                   ))


@user_passes_test(can_manage_library)
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


@user_passes_test(can_manage_library)
def video_folder_add(request, id=None):
    response = folder_add(request, LIBRARY_TYPE_VIDEO, 'media_library/video_folder_add.html', id)
    if response is None:
        return redirect_by_id('media_library:video_index', id)
    return response


@user_passes_test(can_manage_library)
def video_folder_delete(request, id):
    return folder_delete(request, LIBRARY_TYPE_VIDEO, id)


@user_passes_test(can_manage_library)
def video_delete(request, id):
    tree = get_library(LIBRARY_TYPE_VIDEO)
    video = get_document_or_404(File, id=id)
    ids = tree.remove(video)
    tree.save()
    messages.add_message(request, messages.SUCCESS, _('Video successfully removed'))
    return redirect('media_library:video_index')


def audio_index(request):
    return HttpResponse()
