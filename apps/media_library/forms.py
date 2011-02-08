# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.media.forms import PhotoForm, VideoForm

class MediaAddForm(forms.Form):
    name = forms.CharField(label=_("Title"), required=True)
    description = forms.CharField(label=_("Description"), required=True)

class ImageAddForm(PhotoForm, MediaAddForm):
    pass

class VideoAddForm(VideoForm, MediaAddForm):
    pass

class AudioAddForm(MediaAddForm):
    file = forms.FileField(label=_("Audio"))

class FolderEditForm(forms.Form):
    name = forms.CharField(label=_("name"), required=True)