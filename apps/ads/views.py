# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.conf import settings

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from mongoengine.django.shortcuts import get_document_or_404

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
    form = AdsFilterForm(request.GET or None)
    if form.is_valid():
        filter_data = {}
        fields = [
            'country',
            'city',
            'section',
            'category',
            'currency',
            'has_photo',
        ]
        for field in fields:
            if form.cleaned_data[field]:
                filter_data[field] = form.cleaned_data[field]

        if form.cleaned_data['price_from']:
            filter_data['price__gte'] = form.cleaned_data['price_from']

        if form.cleaned_data['price_to']:
            filter_data['price__lte'] = form.cleaned_data['price_to']
        ads = Ad.objects.filter(**filter_data)
    else:
        ads = Ad.objects.all()

    objects = paginate(request, ads, ads.count(), 12)

    return direct_to_template(request, 'ads/list.html',
                              dict(
                                      objects=objects,
                                      form=form,
                                  )
                              )

def edit(request, id=None):
    fields = (
            'country',
            'city',
            'category',
            'section',
            'title',
            'text',
            'price',
            'currency',
            )
    if id:
        ad = get_document_or_404(Ad, id=id, author=request.user)

        initial = {}

        for field in fields:
            initial[field] = getattr(ad, field)

    else:
        ad = None
        initial = {}

    form = AdForm(request.POST or None, request.FILES or None, initial=initial)

    if form.is_valid():
        ad = ad or Ad(author=request.user)
        for field in fields:
            setattr(ad, field, form.cleaned_data[field])

        if request.FILES.has_key('photo'):
            ad.photo = form.fields['photo'].save('ad_photo',
                                     settings.AD_PHOTO_SIZES, 'AD_PHOTO_RESIZE')

        ad.save()

        if id:
            messages.add_message(request, messages.SUCCESS,
                                 _('Ad successfully edited'))
        else:
            messages.add_message(request, messages.SUCCESS,
                             _('Ad successfully added'))

        return redirect('ads:view', id=ad.id)

    return direct_to_template(request, 'ads/edit.html',
                                dict(
                                      form=form,
                                      is_new=id is None
                                      )
                              )


def view(request, id):
    item = get_document_or_404(Ad, id=id)
    return direct_to_template(request, 'ads/view.html',
                                dict(
                                      item=item,
                                      )
                              )

def delete(request, id):
    item = get_document_or_404(Ad, id=id, author=request.user)
    if item.photo:
        item.photo.full_delete()
    item.delete()
    messages.add_message(request, messages.SUCCESS,
                             _('Ad successfully deleted'))

    return redirect('ads:list')
