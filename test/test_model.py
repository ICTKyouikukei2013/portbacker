#coding: utf-8

import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import unittest
from pymongo import Connection

import model


class ModelTest(unittest.TestCase):
    def setUp(self):
        db = Connection('localhost', 27017).testdata
        model.db = db
        db[model.COL_GOALS].drop()
        db[model.COL_PERSONALLOGS].drop()

    def test_insert_goal_text(self):
        u = "morohara"
        gt = u"PHPマスターする"

        goal_texts = model.get_goal_texts(u)
        self.assertFalse(gt in goal_texts)

        model.insert_goal_text(u, gt)
        goal_texts = model.get_goal_texts(u)
        self.assertTrue(gt in goal_texts)

    def test_remove_goal_text(self):
        u = "morohara"
        gt = u"PHPマスターする"

        model.insert_goal_text(u, gt)
        goal_texts = model.get_goal_texts(u)
        self.assertTrue(gt in goal_texts)

        model.remove_goal_text(u, gt)
        goal_texts = model.get_goal_texts(u)
        self.assertFalse(gt in goal_texts)

class UserTest(unittest.TestCase):
    def test_init(self):
        u = model.User("morohara", "b1012187", ["高度ICT演習教育系"], "情報システム", "B2")

    def test_insert(self):
        db = Connection('localhost', 27017).testdata
        model.User.delete_all(db)        
        u = model.User("morohara", "b1012187", ["高度ICT演習教育系"], "情報システム", "B2")
        u.insert(db)

    def test_find(self):
        db = Connection('localhost', 27017).testdata
        model.User.delete_all(db)
        u = model.User("morohara", "b1012187", ["高度ICT演習教育系"], "情報システム", "B2")
        u.insert(db)
        act = model.User.find(db, "b1012187")
        self.assertTrue(act != None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()