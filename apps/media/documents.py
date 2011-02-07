# -*- coding: utf-8 -*-

from datetime import datetime

import pymongo.dbref

from mongoengine import Document

from mongoengine import ReferenceField
from mongoengine import DateTimeField
from mongoengine import FileField
from mongoengine import DictField
from mongoengine import StringField
from mongoengine import ListField

class File(Document):
    author = ReferenceField('User')
    type = StringField(regex='^\w+$', required=True)
    ctime = DateTimeField()
    file = FileField()

    source = ReferenceField('File')
    transformation = StringField()

    name = StringField()
    description = StringField()

    meta = {
        'indexes': [
                'author',
                'type',
                'source',
                'transformation'
        ],
    }

    class SourceFileEmpty(Exception):
        pass

    class ContentTypeUnspecified(Exception):
        pass

    class DerivativeNotFound(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.ctime = self.ctime or datetime.now()

    def save(self, *args, **kwargs):
        if self.file.read() is None:
            raise File.SourceFileEmpty()

        if self.file.content_type is None:
            raise File.ContentTypeUnspecified()

        super(File, self).save(*args, **kwargs)


    def apply_transformations(self, *transformations):
        derivatives = {}

        for transformation in transformations:
            derivatives[transformation.name] = transformation.apply(self)

        return derivatives

    def get_derivative(self, transformation_name):
        derivative = File.objects(source=self, transformation=transformation_name).first()

        if not derivative:
            raise File.DerivativeNotFound()

        return derivative

    class DerivativeProxy(object):
        def __init__(self, file):
            self.file = file

        def __getitem__(self, item):
            return self.file.get_derivative(item)

    def __getattribute__(self, item):
        if item == 'modifications':
            return File.DerivativeProxy(self)
        return super(File, self).__getattribute__(item)


class FileSet(Document):
    author = ReferenceField('User')
    name = StringField()
    type = StringField(regex='^\w+$', required=True)
    files = ListField(ReferenceField(File))

    meta = {
        'indexes': [
                'author',
                'type',
        ],
    }


    def add_file(self, file):
        self.files.append(file)
        self.__class__.objects(id=self.id).update_one(push__files=file)

    def remove_file(self, file):
        self.files.remove(file)
        self.__class__.objects(id=self.id).update_one(pull__files=file)



class Folder(Document):
    name = StringField()


class Tree(Document):
    name = StringField()
    root = DictField(default=lambda: { "data": [] })

    def get_data(self):
        return self.root["data"]

    def add(self, item, folder=None):
        is_folder = isinstance(item, Folder)
        data = [ item.id, item.name, is_folder ]
        if is_folder:
            data.append([])
        items = self.get_data()
        if folder:
            node = self.get(folder.id)
            for n in node.ancestors + [ node ]:
                for i in items:
                    if i[0] == n.id:
                        items = i[3]
                        break
        items.append(data)

    def remove(self, item):
        items = self.get_data()
        node = self.get(item.id)
        for n in node.ancestors:
            for i in items:
                if i[0] == n.id:
                    items = i[3]
                    break
        ids = self.get_children_ids(node) if node.is_folder else []
        items.remove(node.data)
        return [node.id] + ids

    def clear(self):
        self.root["data"] = []

    def get(self, id):
        def search(items, ancestors=[]):
            for item in items:
                node = TreeNode(item, ancestors)
                if node.id == id:
                    return node
                if node.is_folder:
                    el = search(node.children, ancestors + [node])
                    if el:
                        return el
        return search(self.get_data())

    def get_children_ids(self, node):
        ids = []
        def search(items):
            for node in items:
                ids.append(node.id)
                if node.is_folder:
                    search(node.get_children())
        search(node.get_children())
        return ids

    def get_children(self):
        return [TreeNode(i) for i in self.get_data()]


class TreeNode(object):

    def __init__(self, item, ancestors=[]):
        if len(item) == 3:
            item.append(None)
        self.id, self.name, self.is_folder, self.children = item
        self.ancestors = ancestors
        self.data = item

    def get_children(self):
        return [TreeNode(i) for i in self.children]

    def get_document(self):
        if self.is_folder:
            return Folder.objects.get(id=self.id)
        else:
            return File.objects.get(id=self.id)