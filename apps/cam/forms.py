# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Camera, CameraType
from .drivers.base import Driver as BaseDriver
from .drivers.exceptions import ImproperlyConfigured, AccessDenied


class CameraTypeForm(forms.Form):
    name = forms.CharField()
    driver = forms.CharField()

    def clean_driver(self):
        driver = self.cleaned_data['driver']
        camera_type = CameraType(driver=driver)
        try:
            driver_class = camera_type.driver_class
            assert issubclass(driver_class, BaseDriver)
        except:
            raise forms.ValidationError(_('Invalid driver name %(driver)s' % dict(driver=driver)))
        return driver


class CameraForm(forms.Form):
    name = forms.CharField()
    type = forms.ChoiceField(choices=())
    host = forms.CharField()
    username = forms.CharField()
    password = forms.CharField()
    enabled = forms.BooleanField(required=False)
    public = forms.BooleanField(required=False)
    free = forms.BooleanField(required=False)
    operator = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(CameraForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = tuple(
                            (x.id, x.name) for x in CameraType.objects.all())

    def tmp_disabled_clean(self):
        data = self.cleaned_data
        args = dict([(x, data[x]) for x in 'name host username password'.split()])
        args['type'] = CameraType.objects.get(id=data['type'])
        cam = Camera(**args)
        try:
            cam.driver.control.check()
        except AccessDenied:
            raise forms.ValidationError(_('Invalid camera credentials'))
        except ImproperlyConfigured:
            raise forms.ValidationError(_('Camera improperly configured'))
        return self.cleaned_data
