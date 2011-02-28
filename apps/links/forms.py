# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class LinkCategoryForm(forms.Form):
    title = forms.CharField(label=_("Category title"), max_length=50)


class LinkForm(forms.Form):
    title = forms.CharField(label=_("Title"), max_length=50)
    url = forms.URLField(label=_("Url"))
    category = forms.ChoiceField(label=_('Link category'))
