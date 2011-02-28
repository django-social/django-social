# -*- coding: utf-8 -*-

from django.views.generic.simple import direct_to_template
from django.core.paginator import Paginator
from django.conf import settings

from .documents import Ad
from .forms import AdForm, AdsFilterForm

def ajax_get_cities(request):
    pass

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