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
        if form.is_valid():

            file.category = LibraryFileCategory.objects.get(id=
                form.cleaned_data['category'])
            file.name = form.cleaned_data['name']
            file.description = form.cleaned_data['description']

            uploaded_file = request.FILES.get('file')

            if uploaded_file:
                file.file.delete()
                _write_uploaded_file(file, uploaded_file)

            file.save()
            messages.add_message(request, messages.SUCCESS,
                                 _('File successfully updated'))

    else:
        form = FileForm(initial=initial)


    return direct_to_template(request, 'file_library/file_edit.html',
        dict(form=form))


@permission_required('superuser')
def add_file(request):
    if request.POST:
        form = FileForm(request.POST,
                      request.FILES)
    else:
        form = FileForm()

    if form.is_valid():
        file = LibraryFile(type='file_library')

        _write_uploaded_file(file, request.FILES['file'])

        file.transformation ='file'

        file.category = LibraryFileCategory.objects.get(id=
             form.cleaned_data['category'])
        file.name = form.cleaned_data['name']
        file.description = form.cleaned_data['description']
        file.save()
        messages.add_message(request, messages.SUCCESS,
                             _('File successfully added'))

        return redirect('file_library:add_file')

    return direct_to_template(request, 'file_library/file_edit.html',
        dict(form=form))

def _write_uploaded_file(file, uploaded_file):
    buffer = StringIO()
    for chunk in uploaded_file.chunks():
        buffer.write(chunk)

    buffer.seek(0)
    file.file.put(buffer, content_type=uploaded_file.content_type)
    if uploaded_file.name and uploaded_file.name.find('.') != -1:
        file.extension = uploaded_file.name.split('.')[-1]


def index(request):
    files = LibraryFile.objects()
    categories = LibraryFileCategory.objects.all()
    extensions = LibraryFile.objects.distinct('extension')

    return direct_to_template(request, 'file_library/index.html',
                              dict(can_manage=request.user.has_perm('superuser'),
                                   files=files,
                                   categories=categories,
                                   extensions=extensions,
                                   ))

def category_view(request, id):
    category = get_document_or_404(LibraryFileCategory, id=id)
    files = LibraryFile.objects().filter(category=category)
    categories = LibraryFileCategory.objects.all()
    extensions = LibraryFile.objects.distinct('extension')

    return direct_to_template(request, 'file_library/index.html',
                              dict(can_manage=request.user.has_perm('superuser'),
                                   files=files,
                                   categories=categories,
                                   category=category,
                                   extensions=extensions,
                                   ))


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
