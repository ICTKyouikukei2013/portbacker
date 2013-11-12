#coding: utf-8

import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import unittest
from pymongo import Connection

import model
        
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

    def test_find_user_ids_by_joining_group(self):
        db = Connection('localhost', 27017).testdata
        model.User.delete_all(db)
        u1 = model.User("morohara", "b1012187", ["高度ICT演習教育系"], "情報システム", "B2")
        u1.insert(db)
        u2 = model.User("okawara", "b1012555", ["高度ICT演習教育系"], "知能システム", "B3")
        u2.insert(db)
        u3 = model.User("kurosu", "b1012999", ["高度ICT演習事務系"], "情報システム", "B4")
        u3.insert(db)        
        
        act1 = model.User.find_user_ids_by_joining_group(db, u"高度ICT演習教育系")
        self.assertTrue(act1 == ["b1012187", "b1012555"])
        act2 = model.User.find_user_ids_by_joining_group(db, u"高度ICT演習事務系")
        self.assertTrue(act2 == ["b1012999"])
        act3 = model.User.find_user_ids_by_joining_group(db, u"高度ICT演習海洋系")
        self.assertTrue(act3 == [])                



class GroupTest(unittest.TestCase):
    def test_init(self):
        g1 = model.Group("tos_kamiya FanClub", "Kamiya")

    def test_insert(self):
        db = Connection('localhost', 27017).testdata
        model.Group.delete_all(db)
        g1 = model.Group("tos_kamiya FanClub","Kamiya")
        g1.insert(db)

    def test_find(self):
        db = Connection('localhost', 27017).testdata
        model.Group.delete_all(db)
        g1 = model.Group("tos_kamiya FanClub", "Kamiya")
        g2 = model.Group("ObaClub", "Oba")
        g1.insert(db)
        g2.insert(db)
        act1 = model.Group.find(db, "Kamiya")
        act2 = model.Group.find(db, "Oba")
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None)                                                                       

class GoalTest(unittest.TestCase):
    def test_init(self):
        t1 = model.Goal("b1012193", "test title")

    def test_insert(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t1 = model.Goal("b1012193", "test title")
        t1.insert(db)

    def test_insert_duplication(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t2 = model.Goal("b1012193", "test title")
        t2.insert(db)
        with self.assertRaises(model.GoalDuplicationError):
            t2.insert(db)

    def test_find(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t1 = model.Goal("b1012193", "test title")
        t2 = model.Goal("b1012193", "test title1")
        t1.insert(db)
        t2.insert(db)
        act1 = model.Goal.find(db, "b1012193", "test title")
        act2 = model.Goal.find(db, "b1012193", "test title1")
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None)    
        
        
class GoalItemTest(unittest.TestCase):
    def test_init(self):
        i1 = model.GoalItem("b1012193", "test goal", "test title", "testdata",False)

    def test_insert(self):
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012193", "test goal", "test title", "testdata",False)
        i1.insert(db)

    def test_insert_duplication(self):
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012193", "test goal", "test title", "testdata",False)
        i1.insert(db)
        with self.assertRaises(model.GoalItemDuplicationError):
            i1.insert(db)


    def test_find(self):
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012193", "test goal", "test title", "testdata",False)
        i2 = model.GoalItem("b1012193", "test goal1", "test title1", "testdata1",False)
        i1.insert(db)
        i2.insert(db)
        act1 = model.GoalItem.find(db, "b1012193", "test goal", "test title")
        act2 = model.GoalItem.find(db, "b1012193", "test goal1", "test title1")
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None) 


class ItemLogTest(unittest.TestCase):
    def test_init(self):
        i1 = model.ItemLog("b1012193", "test goal", "test goal_item", "2013/11/11", "hogehoge")

    def test_insert(self):
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        i1 = model.ItemLog("b1012193", "test goal", "test goal_item", "2013/11/11", "hogehoge")
        number = i1.insert(db)
        self.assertTrue(number >= 1)


    def test_find(self):
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        i1 = model.ItemLog("b1012193", "test goal", "test goal_item","2013/11/11", "hogehoge")
        i2 = model.ItemLog("b1012193", "test goal1", "test goal_item1","2013/11/11", "hogehoge1")
        number1 = i1.insert(db)
        self.assertTrue(number1 == 1)
        number2 = i2.insert(db)
        self.assertTrue(number2 == 2)
        act1 = model.ItemLog.find(db, "b1012193", number1)
        act2 = model.ItemLog.find(db, "b1012193", number2)
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None) 


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
