# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template

from .documents import Link, LinkCategory
from .forms import LinkForm, LinkCategoryForm

def list(request):
    link_category_form = LinkCategoryForm(request.POST or None)
    link_form = LinkForm(request.POST or None)

    if request.POST:
        if link_category_form.is_valid():
            pass

    user = request.user
    categories = LinkCategory.objects(author=user)
    links = Link.objects(author=user)
    return direct_to_template(request, "links/list.html",
                              dict(
                                    categories=categories,
                                    links=links,
                                    link_category_form=link_category_form,
                                    link_form=link_form,
                                   )
                              )