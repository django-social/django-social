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

from apps.media.documents import File
from apps.utils.stringio import StringIO


from .forms import ApplicationForm
from .documents import Application


def can_manage_applications(user):
     return user.has_perm('applications')


def list(request):
    form = ApplicationForm()
    items = Application.objects()
    form = ApplicationForm()
    objects = paginate(request,
                       items,
                       len(items),
                       settings.APPLICATIONS_PER_PAGE
                       )

    return direct_to_template(request, 'applications/list.html',
                              dict(
                                      objects=objects,
                                      can_manage=can_manage_applications(request.user),
                                      form=form,
                                   )

                              )
@user_passes_test(can_manage_applications)
def add(request):
    if request.POST:
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = Application()
            application.image = form.fields['image'].save('application_image',
                                                          settings.APPLICATION_IMAGE_SIZES,
                                                          'APPLICATION_IMAGE_RESIZE'
                    )

            application.file = _make_swf(request.FILES['file'])

            application.name = form.cleaned_data['name']
            application.description = form.cleaned_data['description']
            application.save()

            messages.add_message(request, messages.SUCCESS,
                                 _('Application successfully added'))

            return redirect('applications:list')

    else:
        form = ApplicationForm()
    return direct_to_template(request, 'applications/list.html',
                              dict(form=form,
                                   can_manage=True,

                                   )
                              )


def view(request, id):
    app = get_document_or_404(Application, id=id)
    return direct_to_template(request, 'applications/view.html', dict(app=app) )

@user_passes_test(can_manage_applications)
def delete(request, id):
    app = get_document_or_404(Application, id=id)

    app.delete()

    messages.add_message(request, messages.SUCCESS,
                         _('Application successfully removed'))

    return redirect('applications:list')


def _make_swf(file):
    buffer = StringIO()
    for chunk in file.chunks():
        buffer.write(chunk)

    buffer.reset()

    file = File(type='application_swf')
    file.file.put(buffer, content_type='application/x-shockwave-flash')
    file.transformation = 'main.swf'
    file.save()
    return file


@user_passes_test(can_manage_applications)
def edit(request, id):
    app = get_document_or_404(Application, id=id)
    if request.POST:
        form = ApplicationForm(request.POST, request.FILES)
    else:
        form = ApplicationForm(initial=app._data)

    form.fields['file'].required = False
    form.fields['image'].required = False


    if form.is_valid():
        need_save = False

        if request.FILES.has_key('file'):
            app.file = _make_swf(request.FILES['file'])
            need_save = True

        if request.FILES.has_key('image'):
            app.image = form.fields['image'].save('application_image',
                                                          settings.APPLICATION_IMAGE_SIZES,
                                                          'APPLICATION_IMAGE_RESIZE'
                    )

            need_save = True

        for attr in ('name', 'description'):
            if getattr(app, attr) != form.cleaned_data[attr]:
                setattr(app, attr, form.cleaned_data[attr])
                need_save = True
                
        if need_save:
            app.save()
        
    #messages.add_message(request, messages.SUCCESS,
    #                     _('Application successfully updated'))

    return direct_to_template(request, 'applications/edit.html',
                              dict(app=app,
                                   form=form,
                                   can_manage=True
                                   ))

    return redirect('applications:list')
