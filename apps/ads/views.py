# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template

from .documents import Ad

def ajax_get_cities(request):
    pass

def list(request):
    items = Ad.objects.all()
    return direct_to_template(request, 'ads/list.html',
                              dict(items=items,)
                              )