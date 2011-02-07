# -*- coding: utf-8 -*-
from apps.utils.paginator import paginate
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
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


def image_index(request):
    tree = get_library(LIBRARY_TYPE_IMAGE)
    can_manage = can_manage_library(request.user)
    if can_manage:
        form = ImageAddForm()
    else:
        form = None

    items = tree.get_children()

    objects = paginate(request,
                       items,
                       len(items),
                       settings.LIBRARY_IMAGES_PER_PAGE
                       )

    return direct_to_template(request, 'media_library/image_index.html',
                              dict(
                                      objects=objects,
                                      form=form,
                                      can_manage=can_manage,
                                   )
                              )


@user_passes_test(can_manage_library)
def image_add(request):
    form = ImageAddForm(request.POST, request.FILES)

    if form.is_valid():
        tree = get_library(LIBRARY_TYPE_IMAGE)
        file = form.fields['file'].save('library_image', settings.LIBRARY_IMAGE_SIZES, LIBRARY_IMAGE_RESIZE_TASK)

        file.name = form.cleaned_data['name']
        file.description = form.cleaned_data['description']
        file.save()

        tree.add(file)
        tree.save()
        messages.add_message(request, messages.SUCCESS, _('Image successfully added'))
    return redirect('media_library:image_index')


def folder_add(request, tree_id):
    form = FolderEditForm(request.POST)

    if form.is_valid():
        tree = get_library(LIBRARY_TYPE_IMAGE)

        folder = Folder(name=form.cleaned_data['name'])
        folder.save()

        tree.add(folder)
        tree.save()
        messages.add_message(request, messages.SUCCESS, _('Image successfully added'))
    return redirect('media_library:image_index')


@user_passes_test(can_manage_library)
def image_delete(request, id):
    tree = get_library(LIBRARY_TYPE_IMAGE)
    image = get_document_or_404(File, id=id)
    ids = tree.remove(image)
    tree.save()
    messages.add_message(request, messages.SUCCESS, _('Image successfully removed'))
    return redirect('media_library:image_index')


def video_index(request):
    tree = get_library(LIBRARY_TYPE_VIDEO)
    if can_manage_library(request.user):
        form = VideoAddForm()
    else:
        form = None

    items = tree.get_children()

    objects = paginate(request,
                       items,
                       len(items),
                       settings.LIBRARY_VIDEO_PER_PAGE
                       )

    return direct_to_template(request, 'media_library/video_index.html',
                              dict(objects=objects,form=form,
                                      can_manage=can_manage_library(request.user),
                                   ))


@user_passes_test(can_manage_library)
def video_add(request):
    form = VideoAddForm(request.POST, request.FILES)
    if form.is_valid():
        tree = get_library(LIBRARY_TYPE_VIDEO)
        file = form.fields['file'].save('library_video', settings.LIBRARY_VIDEO_SIZES,
                                        LIBRARY_VIDEO_RESIZE_TASK)

        file.name = form.cleaned_data['name']
        file.description = form.cleaned_data['description']
        file.save()

        tree.add(file)
        tree.save()

        messages.add_message(request, messages.SUCCESS, _('Video successfully added'))
    else:
        print form.errors

    return redirect('media_library:video_index')


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
