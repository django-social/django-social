# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from mongoengine import (Document, StringField, ReferenceField,
                         BooleanField, DateTimeField, IntField)

class Ad(Document):
    creation_time = DateTimeField(default=datetime.now)

    title = StringField()
    text = StringField()

    section = StringField()
    category = StringField()

    country = StringField()
    city = StringField()

    price = IntField()
    currency = StringField()

    photo = ReferenceField('File')
