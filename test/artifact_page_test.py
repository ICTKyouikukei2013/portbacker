#coding: utf-8

from flask import Request

import os
import shutil
import sys
from cStringIO import StringIO
import unittest

sys.path.insert(0, "..")  # portfolio.pyにパスを通す

import portfolio

# ref https://gist.github.com/lost-theory/3772472

class ArtifactPageTest(unittest.TestCase):
    def setUp(self):
        self.app = app = portfolio.app
        app.debug = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_uploading(self):
        data_dir = portfolio.UPLOAD_FOLDER
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        file_name = 'hello.txt'
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        rv = self.client.post('/artifact',
            data={
                  'file': (StringIO('hello world!'), file_name),
            })

        self.assertTrue(file_name in rv.data)
        self.assertTrue(os.path.exists(file_path))

        os.remove(file_path)

    def test_unploading_non_allowed_file(self):
        data_dir = portfolio.UPLOAD_FOLDER
        file_name = 'A.java'
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

        rv = self.client.post('/artifact',
            data={
                  'file': (StringIO('import java.util.*;'), file_name),
            })

        self.assertTrue(not os.path.exists(file_path))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()