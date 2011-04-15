# -*- coding: utf-8 -*-
from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import StringField

from apps.media.documents import File


class LibraryFileCategory(Document):
    title = StringField(required=True)


class LibraryFile(File):
    category = ReferenceField(LibraryFileCategory)

