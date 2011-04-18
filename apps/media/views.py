# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.conf import settings
from django.utils.encoding import iri_to_uri

from pytils.translit import translify

from documents import File


def file_view(request, transformation_name, file_id=None):
    return _file_view(request, transformation_name, file_id)

def file_download(request, transformation_name, file_id=None):
    return _file_view(request, transformation_name, file_id, download=True)


def _file_view(request, transformation_name, file_id=None, download=False):
    not_found_path = '%snotfound/%s'
    converting_path = '%sconverting/%s'
    if file_id:
        try:
            file = File.objects.get(id=file_id)
        except File.DoesNotExist:
            file = None
            raise Http404()

        else:
            try:
                modification = file.modifications[transformation_name]
            except File.DerivativeNotFound:
                modification = None
    else:
        file = None
        modification = None

    if modification:
        response = HttpResponse(modification.file.read(),
            content_type='application/octet-stream' if download
                else
            modification.file.content_type
        )
        response['Last-Modified'] = modification.file.upload_date
        if download:
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            file_name = (file.name or str(file.id)) + ('.%s' % file.extension
                                                    if file.extension else '')

            file_name = translify(file_name)
            if 0: #TODO
                file_name = iri_to_uri(file_name)

                if user_agent.find('opera') == -1:
                    pass
                if user_agent.find('msie') != -1:
                    file_name.replace('+', '%20')

            response['Content-Disposition'] = 'attachment; filename="%s";' % file_name


        return response

    if file and os.path.exists(converting_path %
                    (settings.MEDIA_ROOT, transformation_name)):
        return redirect(converting_path %
                (settings.MEDIA_URL, transformation_name))


    if os.path.exists(not_found_path %
                    (settings.MEDIA_ROOT, transformation_name)):
        return redirect(not_found_path %
                    (settings.MEDIA_URL, transformation_name))

    raise Http404()