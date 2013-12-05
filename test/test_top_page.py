#coding: utf-8

import sys
import unittest

import os.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import portfolio
import model

class TopPageTest(unittest.TestCase):
    def setUp(self):
        model.User.delete_all(model.db)
        self.u = model.User("Hoge Ratta", "b1010999", None, u'情報システム', 'B4')
        self.u.insert(model.db)
        app = portfolio.app
        app.debug = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_login_by_registered_user(self):
        rv = self.client.post('/login', data=dict(
                username='b1010999', password='hogehoge'),
                follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(u'<title>E-portfolio</title>' in rv.data.decode('utf-8'))  # top page

    def test_login_by_unregistered(self):
        rv = self.client.post('/login', data=dict(
                username='unregistered', password='hogehoge'),
                follow_redirects=True)
        self.assertTrue(u'<div class="prof">' in rv.data.decode('utf-8'))  # user profile registration page
        rv = self.client.get('/logout', follow_redirects=True)

    def test_access_before_login(self):
        with self.client.session_transaction() as sess:
            sess['username'] = None
        rv = self.client.get('/', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(u'<div class="loginbox">' in rv.data.decode('utf-8'))  # login page

        rv = self.client.get('/goal', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertTrue(u'<div class="loginbox">' in rv.data.decode('utf-8'))  # login page

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()