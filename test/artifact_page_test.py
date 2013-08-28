#coding: utf-8

from flask import Request

import sys
from cStringIO import StringIO
import unittest

import os.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import portfolio

# ref https://gist.github.com/lost-theory/3772472

class ArtifactPageTest(unittest.TestCase):
    def setUp(self):
        self.app = app = portfolio.app
        app.debug = True
        self.client = app.test_client()
        data_dir = portfolio.UPLOAD_FOLDER
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        self.data_dir = data_dir

    def tearDown(self):
        pass

    def test_get_page(self):
        rv = self.client.get('/artifact')
        assert rv.status_code == 200
        
    def test_uploading(self):
        file_name = 'hello.txt'
        file_path = os.path.join(self.data_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        rv = self.client.post('/artifact',
            data={
                  'file': (StringIO('hello world!'), file_name),
                  'directoryname': None
            })
        assert rv.status_code == 200
        self.assertTrue(file_name in rv.data)
        self.assertTrue(os.path.exists(file_path))

        os.remove(file_path)

    def test_unploading_non_allowed_file(self):
        file_name = 'A.java'
        file_path = os.path.join(self.data_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        rv = self.client.post('/artifact',
            data={
                  'file': (StringIO('import java.util.*;'), file_name),
                  'directoryname': None
            })

        self.assertTrue(not os.path.exists(file_path))

    def test_make_new_dir(self):
        new_dir_name = "testdir-hogehoge"
        dir_path = os.path.join(self.data_dir, new_dir_name)
        if os.path.exists(dir_path):
            assert os.path.isdir(dir_path)
            os.rmdir(dir_path)

        rv = self.client.post('/artifact',
            data={
                  'file': (None, ''),
                  'directoryname': new_dir_name
            })

        assert rv.status_code == 200
        self.assertTrue(os.path.exists(dir_path))

        os.rmdir(dir_path)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()