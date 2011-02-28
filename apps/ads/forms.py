# -*- coding: utf-8 -*-

from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext_lazy as _

from choices import geo_data, currency_data, type_ads
#simplejson.dumps(c, ensure_ascii=False)

class AdsFilterForm(forms.Form):
    country = forms.ChoiceField(label=_('Country'), choices=tuple([(u'', u''),]+[ (x, x) for x in geo_data.keys() ]))
    city = forms.ChoiceField(label=_('City'))
    section = forms.ChoiceField(label=_('Section'), choices=tuple([(u'', u''),]+[ (x, x) for x in type_ads.keys() ]))
    category = forms.ChoiceField(label=_('Category'))
    price = forms.FloatField(label=_('Price'))
    currency = forms.ChoiceField(label=_('Currency'), choices=tuple([ (x, x) for x in currency_data ]))
    has_photo = forms.BooleanField(label=_('Has photo'), required=False)


class AdForm(forms.Form):
    country = forms.ChoiceField(label=_('Country'),
                                choices=tuple([(u'', u''),]+[ (x, x) for x in geo_data.keys() ]))

    city = forms.ChoiceField(label=_('City'))

    section = forms.ChoiceField(label=_('Section'),
                                choices=tuple([(u'', u''),]+[ (x, x) for x in type_ads.keys() ]))

    category = forms.ChoiceField(label=_('Category'))
    price = forms.FloatField(label=_('Price'))
    currency = forms.ChoiceField(label=_('Currency'),
                                 choices=tuple([ (x, x) for x in currency_data ]))

    title = forms.CharField(label=_('Title'))
    text = forms.CharField(label=_('Text'), widget=forms.Textarea)

    photo = forms.FileField(label=_('Photo'), required=False)

    def __init__(self, data, *args, **kwargs):
        super(AdForm, self).__init__(data, *args, **kwargs)
        if data:
            country = data.get('country')
            self.fields['city'].choices = tuple([(u'', u''),] + [(x, x)
                                             for x in geo_data.get(country, [])])
            section = data.get('section')
            self.fields['category'].choices = tuple([(u'', u''),] + [(x, x)
                                             for x in type_ads.get(section, [])])

