# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template

from .documents import Ad
from .forms import AdForm

def ajax_get_cities(request):
    pass

def list(request):
    items = Ad.objects.all()
    return direct_to_template(request, 'ads/list.html',
                              dict(items=items,)
                              )

def add(request):
    form = AdForm(request.POST or None)
    return direct_to_template(request, 'ads/edit.html',
                                dict(
                                      form=form,
                                      )
                              )

def edit(request, id):
    pass

def view(request, id):
    pass