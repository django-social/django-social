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
            buffer = StringIO()
            for chunk in request.FILES['file'].chunks():
                buffer.write(chunk)

            buffer.reset()

            file = File(type='application_swf')
            file.file.put(buffer, content_type='application/x-shockwave-flash')
            file.transformation = 'main.swf'
            file.save()

            application.file = file

            application.name = form.cleaned_data['name']
            application.description = form.cleaned_data['description']
            application.save()

            messages.add_message(request, messages.SUCCESS, _('Application successfully added'))
            return redirect('applications:list')

    else:
        form = ApplicationForm()
    return direct_to_template(request, 'media_library/image_add.html', dict(form=form) )


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
