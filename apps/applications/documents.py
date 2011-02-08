# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField

class Application(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    file = ReferenceField('File')
    image = ReferenceField('File')

