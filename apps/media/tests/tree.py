# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.conf import settings
from .common import file_path, create_image_file

from ..documents import Tree, File, Folder, TreeNode


class TreeTest(TestCase):

    def setUp(self):
        self.cleanUp()

    def cleanUp(self):
        File.objects.delete()
        Folder.objects.delete()
        Tree.objects.delete()

    def tearDown(self):
        #self.cleanUp()
        pass

    def test_add_file(self):
        tree = Tree()
        tree.save()
        file = create_image_file()
        tree.add(file)
        tree.save()
        tree.reload()
        self.failUnless([ file.id, file.name,  False ] in tree.root["data"])
        node = tree.get(file.id)
        self.failUnless(isinstance(node, TreeNode))
        self.failIf(node.is_folder)

    def test_add_folder(self):
        tree = Tree()
        tree.save()
        folder1 = Folder(name="folder1")
        folder1.save()
        tree.add(folder1)
        tree.save()
        tree.reload()
        self.failUnless([ folder1.id, folder1.name,  True, [] ] in tree.root["data"])
        node = tree.get(folder1.id)
        self.failUnless(isinstance(node, TreeNode))
        self.failUnless(node.is_folder)
        self.failUnless(isinstance(node.ancestors, list))

    def test_folder_add_file(self):
        tree = Tree()
        tree.save()
        folder1 = Folder(name="folder1")
        folder1.save()
        tree.add(folder1)
        file = create_image_file()
        tree.add(file, folder1)
        tree.save()
        tree.reload()
        node = tree.get(file.id)
        self.failUnless(len(node.ancestors) == 1)

        folder2 = Folder(name="folder2")
        folder2.save()
        tree.add(folder2, folder1)
        file = create_image_file()
        tree.add(file, folder2)
        tree.save()
        tree.reload()
        node = tree.get(file.id)
        self.failUnless(len(node.ancestors) == 2)

    def test_remove_file(self):
        tree = Tree()
        tree.save()
        folder1 = Folder(name="folder1")
        folder1.save()
        tree.add(folder1)
        folder2 = Folder(name="folder2")
        folder2.save()
        tree.add(folder2, folder1)
        file = create_image_file()
        tree.add(file, folder2)
        tree.save()
        tree.reload()

        self.failUnless(len(tree.remove(folder2)) == 2)
        tree.save()
        self.failUnless([[ folder1.id, folder1.name,  True, [] ]] == tree.root["data"])