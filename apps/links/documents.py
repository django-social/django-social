# -*- coding: utf-8 -*-
from datetime import datetime

from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField
from mongoengine.fields import DateTimeField, URLField

class LinkCategory(Document):
    author = ReferenceField('User')
    title = StringField()
    creation_time = DateTimeField(default=datetime.now)

class Link(Document):
    author = ReferenceField('User')
    category = ReferenceField('LinkCategory')
    url = URLField()
    creation_time = DateTimeField(default=datetime.now)

