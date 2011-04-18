# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from .documents import LibraryFileCategory, LibraryFile


class FileForm(forms.Form):
    category = forms.ChoiceField(label=_('Category'), choices=())
    file = forms.FileField(label=_("File"), required=True)
    name = forms.CharField(label=_("Title"), required=True)
    description = forms.CharField(label=_("Description"), required=False)

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = tuple(
            [('', _('Select category')), ] +
            [(x.id, x.title)
                           for x in LibraryFileCategory.objects])

class FileCategoryForm(forms.Form):
    title = forms.CharField(label=_("Title"), required=True)

class FilterFileLibraryForm(forms.Form):
    category = forms.ChoiceField(
        label=_('Category'),
        required=False,
        choices=[('', _('All categories'))] + [(category.id, category.title) for category in LibraryFileCategory.objects.all()]
    )

    extension = forms.ChoiceField(
        label=_('Extension'),
        required=False,
        choices=[('', _('All extensions'))] + [(extension, extension) for extension in LibraryFile.objects.distinct('extension')]
    )
