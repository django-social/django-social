# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.utils.simplejson import dumps

from apps.utils.paginator import paginate

from .documents import Ad
from .forms import AdForm, AdsFilterForm
from .choices import geo_data, type_ads

def ajax_get_cities(request):
    country = request.POST.get('country', '')
    if country:
        cities = geo_data[country]
        return HttpResponse(dumps(cities, ensure_ascii=False), mimetype='application/javascript')

def ajax_get_categories(request):
    section = request.POST.get('section', '')
    if section:
        categories = type_ads[section]
        return HttpResponse(dumps(categories), mimetype='application/javascript')

def list(request):
    form = AdsFilterForm(request.POST or None)

    ads = Ad.objects.all()
    objects = paginate(request, ads, ads.count(), 12)

    return direct_to_template(request, 'ads/list.html',
                              dict(
                                      objects=objects,
                                      form=form,
                                  )
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