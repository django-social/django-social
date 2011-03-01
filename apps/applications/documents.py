# -*- coding: utf-8 -*-
from apps.media.documents import File
from django.utils.translation import ugettext_lazy as _

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField

class Application(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    file = ReferenceField('File')
    image = ReferenceField('File')
    flashvars = StringField()

    def delete_files(self):
        self.file.full_delete()
        self.image.full_delete()

    def delete(self, *args, **kwargs):
        self.delete_files()
        return super(Application, self).delete(*args, **kwargs)

