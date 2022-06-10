import os
import shutil
from unittest import mock

from django.test import TestCase
from django.core.files.storage import default_storage

from wordbook_generator.settings.base import MEDIA_ROOT 
from serializer.serializer import Serializer
from tasks.models import Task


class CsvBuilderTest(TestCase):
    fixtures = ['tasks.json', 'morph.json', 'words.json']

    def setUp(self):
        self.task = Task.objects.get(original_file_path='dummy_path1')

    def tearDown(self):
        shutil.rmtree(MEDIA_ROOT)
        os.mkdir(MEDIA_ROOT)

    @mock.patch('serializer.serializer.Serializer._to_csv')
    def test_serialize(self, _to_csv):
        s = Serializer(self.task.id)
        s.serialize()
        _to_csv.assert_called()

    def test_private_to_csv(self):
        s = Serializer(self.task.id)
        path = s._to_csv()
        self.assertTrue(default_storage.exists(path))