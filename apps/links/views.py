# -*- coding: utf-8 -*-
import re

from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _

from .documents import Link, LinkCategory
from .forms import LinkForm, LinkCategoryForm

def list(request):
    user = request.user

    form = request.POST.get('form')


    if request.POST and form in ('category', 'link'):
        if form=='category':
            link_category_form = LinkCategoryForm(request.POST)
            if link_category_form.is_valid():
                title = link_category_form.cleaned_data['title']
                title = re.sub('\s+', ' ', title.strip())
                LinkCategory.objects.get_or_create(title=title, author=user)
                link_category_form = LinkCategoryForm()
            link_form = LinkForm()

        if form=='link':
            link_form = LinkForm(request.POST)
            categories = LinkCategory.objects(author=user)

            link_form.fields['category'].choices = tuple(
                [('', _('Select link category'))] +
                [ (x.id, x.title) for x in categories ]
            )


            if link_form.is_valid():
                url = link_form.cleaned_data['url']
                category_id = link_form.cleaned_data['category']
                category = LinkCategory.objects(id=category_id, author=user).first()
                Link.objects.get_or_create(url=url,
                                           category=category,
                                           author=user)

            link_category_form = LinkCategoryForm()

    else:
        link_form = LinkForm()
        link_category_form = LinkCategoryForm()

    categories = LinkCategory.objects(author=user)

    link_form.fields['category'].choices = tuple(
        [('', _('Select link category'))] +
        [ (x.id, x.title) for x in categories ]
    )
        

    links = Link.objects(author=user)
    

    return direct_to_template(request, "links/list.html",
                              dict(
                                    categories=categories,
                                    links=links,
                                    link_category_form=link_category_form,
                                    link_form=link_form,
                                   )
                              )