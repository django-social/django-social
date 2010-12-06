# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse

from mongoengine.django.shortcuts import get_document_or_404

from .constants import AVAILABLE_COMMANDS

from .documents import Camera
from .documents import CameraType

from .forms import CameraTypeForm, CameraForm
from apps.billing.documents import Tariff
from apps.cam.forms import CamFilterForm
from apps.cam.documents import CameraBookmarks
from django.shortcuts import redirect


#@login_required
def cam_list(request):
    form = CamFilterForm(request.POST or None)
    if form.is_valid():
        data = dict(form.cleaned_data)
        if not data['name']:
            del data['name']
        else:
            data['name__icontains'] = data['name']
            del data['name']
        if not data['is_managed']:
            del data['is_management_enabled']
            del data['is_management_public']
            del data['is_management_paid']
        cams = Camera.objects(**data)
        print data
    else:
        cams = Camera.objects()
    for cam in cams:
        print cam.owner.__class__
    return direct_to_template(request, 'cam/cam_list.html', dict(form=form,cams=cams) )


#@login_required
def cam_edit(request, id=None):
    user = request.user
    if id:
        cam = get_document_or_404(Camera, id=id, owner=user)
        if not user.is_superuser and user.id != cam.owner.id:
            return HttpResponseNotFound()
        initial = cam._data
        initial['type'] = cam.type.get_option_value()
        for tariff_type in Camera.TARIFF_FIELDS:
            value = getattr(cam, tariff_type)
            if value:
                initial[tariff_type] = value.id

    else:
        cam = None
        initial = {}

    form = CameraForm(user, request.POST or None, initial=initial)

    if form.is_valid():
        if not cam:
            cam = Camera()
            cam.owner = user

        for k, v in form.cleaned_data.items():
            setattr(cam, k, v)

        cam.type = CameraType.objects.get(id=form.cleaned_data['type'][:-2])

        for tariff_type in Camera.TARIFF_FIELDS:
            value = form.cleaned_data[tariff_type]
            if value:
                value = Tariff.objects.get(id=value)
                assert value in getattr(Tariff, 'get_%s_list' % tariff_type)()
                setattr(cam, tariff_type, value)
            else:
                setattr(cam, tariff_type, None)

        cam.save()

        return HttpResponseRedirect(reverse('social:home'))

    return direct_to_template(request, 'cam/cam_edit.html',
                              dict(form=form, is_new=id is None)
                              )


#@login_required
def cam_view(request, id):
    cam = get_document_or_404(Camera, id=id)
    return direct_to_template(request, 'cam/cam_view.html',
                              dict(cam=cam)
                              )



@permission_required('superuser')
def type_list(request):
    types = CameraType.objects()
    return direct_to_template(request, 'cam/type_list.html',
                              dict(types=types)
                              )


@permission_required('superuser')
def type_edit(request, id=None):
    if id:
        type = get_document_or_404(CameraType, id=id)
        initial = {}
        for k in type._fields.keys():
            if k in ('id', ):
                continue
            initial[k] = getattr(type, k)
    else:
        type = None
        initial = {}

    form = CameraTypeForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not type:
            type = CameraType()

        for k, v in form.cleaned_data.items():
            if k.startswith('_'):
                continue
            if hasattr(type, k):
                setattr(type, k, v)
        type.save()
        #return HttpResponseRedirect(reverse('cam:type_edit', kwargs=dict(id=type.id)))
        return HttpResponseRedirect(reverse('cam:type_list'))

    return direct_to_template(request, 'cam/type_edit.html',
                              dict(form=form, is_new=id is None)
                              )


@permission_required('superuser')
def type_delete(request, id):
    type = get_document_or_404(CameraType, id=id)
    type.delete()
    return HttpResponseRedirect(reverse('cam:type_list'))


#@login_required
def cam_manage(request, id, command):
    if command not in AVAILABLE_COMMANDS:
        return HttpResponseNotFound()

    cam = get_document_or_404(Camera, id=id)
    cam = Camera()

    return HttpResponse()


#@login_required
def cam_bookmarks(request):
    try:
        bookmarks = CameraBookmarks.objects.get(user=request.user)
    except CameraBookmarks.DoesNotExist:
        cameras = None
    else:
        cameras = bookmarks.cameras
    return direct_to_template(request, 'cam/bookmarks.html', {'cameras': cameras})


#@login_required
def cam_bookmark_add(request, id):
    camera = get_document_or_404(Camera, id=id)
    camera.bookmark_add(request.user)
    #@TODO: show message added
    return redirect(reverse('social:user', args=[camera.owner.id]))


#@login_required
def cam_bookmark_delete(request, id):
    camera = get_document_or_404(Camera, id=id)
    camera.bookmark_delete(request.user)
    #@TODO: show message added
    return redirect(reverse('social:user', args=[camera.owner.id]))