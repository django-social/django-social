# -*- coding: utf-8 -*-
from apps.media.documents import File
from django.utils.translation import ugettext_lazy as _

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField

class Application(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    file = ReferenceField('File')
    image = ReferenceField('File')

    def delete(self, *args, **kwargs):
        self.file.file.delete()
        self.file.delete()

        for file in File.objects(source=self.image):
            file.file.delete()
            file.delete()

        self.image.file.delete()
        self.image.delete()

        return super(Application, self).delete(*args, **kwargs)

