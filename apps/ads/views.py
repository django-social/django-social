# -*- coding: utf-8 -*-
from django.shortcuts import redirect

from django.views.generic.simple import direct_to_template
from django.conf import settings

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
    form = AdForm(request.POST or None, request.FILES)
    if form.is_valid():
        ad = Ad()

        if request.FILES.has_key('photo'):
            ad.photo = form.fields['photo'].save('ad_photo',
                                     settings.AD_PHOTO_SIZES, 'AD_PHOTO_RESIZE')

        ad.save()    
        return redirect('ads:view', id=ad.id)

    return direct_to_template(request, 'ads/edit.html',
                                dict(
                                      form=form,
                                      )
                              )

def edit(request, id):
    pass

def view(request, id):
    pass