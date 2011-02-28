# -*- coding: utf-8 -*-

from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from choices import geo_data, currency_data
#simplejson.dumps(c, ensure_ascii=False)

class AdsFilterForm(forms.Form):
    country = forms.ChoiceField(label=_('Country'), choices=geo_data.keys())
    city = forms.ChoiceField(label=_('City'))
    section = forms.ChoiceField(label=_('Section'), choices=type_ads.keys())
    category = forms.ChoiceField(label=_('Category'))
    price = forms.FloatField(label=_('Price'))
    currency = forms.ChoiceField(label=_('Currency'), choices=currency_data)
    has_photo = forms.BooleanField(label=_('Has photo'), required=False)