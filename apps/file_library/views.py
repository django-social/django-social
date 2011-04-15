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

from .forms import FileForm, FileCategoryForm
from .documents import LibraryFile, LibraryFileCategory

def file_view(request, id):
    file = get_document_or_404(LibraryFile, id=id)
    return direct_to_template(request, 'file_library/file_view.html',
        dict(file=file))

@permission_required('superuser')
def file_delete(request, id):
    file = get_document_or_404(LibraryFile, id=id)
    file.full_delete()
    messages.add_message(request, messages.SUCCESS, _('File successfully deleted'))
    return redirect('file_library:index')

@permission_required('superuser')
def file_edit(request, id):
    file = get_document_or_404(LibraryFile, id=id)
    initial = file._data
    initial['category'] = file.category.id

    if request.POST:
        form = FileForm(request.POST,
                      request.FILES, initial=initial)
        form.fields['file'].required = False

    else:
        form = FileForm(initial=initial)


    return direct_to_template(request, 'file_library/file_edit.html',
        dict(form=form))



def index(request):
    files = LibraryFile.objects()
    categories = LibraryFileCategory.objects.all()

    return direct_to_template(request, 'file_library/index.html',
                              dict(can_manage=request.user.has_perm('superuser'),
                                   files=files,
                                   categories=categories,
                                   ))

def category_view(request, id):
    category = get_document_or_404(LibraryFileCategory, id=id)
    files = LibraryFile.objects().filter(category=category)
    categories = LibraryFileCategory.objects.all()


    return direct_to_template(request, 'file_library/index.html',
                              dict(can_manage=request.user.has_perm('superuser'),
                                   files=files,
                                   categories=categories,
                                   category=category,
                                   ))

@permission_required('superuser')
def add_file(request):
    if request.POST:
        form = FileForm(request.POST,
                      request.FILES)
    else:
        form = FileForm()

    if form.is_valid():
        file = request.FILES['file']

        buffer = StringIO()
        for chunk in file.chunks():
            buffer.write(chunk)

        buffer.seek(0)
        file_object = LibraryFile(type='file_library')
        file_object.file.put(buffer, content_type=file.content_type)
        file_object.transformation ='get'

        file_object.category = LibraryFileCategory.objects.get(id=
                form.cleaned_data['category'])
        file_object.name = form.cleaned_data['name']
        file_object.description = form.cleaned_data['description']
        file_object.save()


        return redirect('file_library:add_file')

    return direct_to_template(request, 'file_library/file_edit.html',
        dict(form=form))

@permission_required('superuser')
def add_category(request):
    form = FileCategoryForm(request.POST or None)

    if form.is_valid():
        object, created = LibraryFileCategory.objects.get_or_create(title=
                form.cleaned_data['title'].strip())
        if created:
            messages.add_message(request, messages.SUCCESS,
                                _('Category successfully added'))
        else:
            messages.add_message(request, messages.WARNING,
                                _('Category already exists'))

        return redirect('file_library:add_category')

    return direct_to_template(request, 'file_library/category_edit.html',
        dict(form=form))
