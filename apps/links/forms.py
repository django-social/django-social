# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class LinkCategoryForm(forms.Form):
    title = forms.CharField(label=_("Category title"), max_length=50)

class LinkForm(forms.Form):
    url = forms.URLField(label=_("Url"))
