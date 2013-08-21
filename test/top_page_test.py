#coding: utf-8
import sys
import unittest

import os.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import portfolio

class TopPageTest(unittest.TestCase):

    def setUp(self):
        self.app = portfolio.app.test_client()

    def tearDown(self):
        pass

    def test_top_page_inclues_links_to_pages(self):
        rv = self.app.get('/')
        self.assertTrue(u'ここはトップページです' in rv.data)
        self.assertTrue(u'href="portfolio"' in rv.data)
        self.assertTrue(u'href="goal"' in rv.data)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()