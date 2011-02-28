# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.conf import settings
from django.utils.simplejson import dumps

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
    ads_list = Ad.objects.all()

    paginator = Paginator(ads_list, settings.ADS_PER_PAGE)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'ads/list.html',
                              dict(
                                      objects=objects,
                                      form=form,
                                  )
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