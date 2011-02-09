# -*- coding: utf-8 -*-
from apps.media.fields import ImageField
from django import forms

from django.utils.translation import ugettext_lazy as _
from mongoengine import Q

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField, DateTimeField, IntField


class ApplicationForm(forms.Form):
    name = forms.CharField(label=_("Title"), required=True)
    description = forms.CharField(label=_("Description"),
                                  required=True,
                                  widget=forms.Textarea(attrs=dict(
                                          rows="10",
                                          cols="40"
                                          )))
    image = ImageField(label=_("Image"))
    file = forms.FileField(label=_("Application"))



