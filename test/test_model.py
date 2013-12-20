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

    def test_update(self):
        db = Connection('localhost', 27017).testdata
        model.User.delete_all(db)
        u = model.User("morohara", "b1012187", ["高度ICT演習教育系"], "情報システム", "B2")
        u.insert(db)
        u2 = model.User("mother", "b1012187", ["高度ICT演習教育系"], "知能システム", "B2")
        u2.update(db)
        act = model.User.find(db, "b1012187")
        self.assertTrue(act.name == "mother")


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
        t1 = model.Goal("b1012100", "test title")

    def test_insert(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t1 = model.Goal("b1012100", "test title")
        t1.insert(db)
        self.assertTrue(t1.serial is not None)

    def test_insert_duplication(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t2 = model.Goal("b1012100", "test title")
        t2.insert(db)
        self.assertTrue(t2.serial is not None)
        with self.assertRaises(model.GoalInsertedTwice):
            t2.insert(db)

    def test_insert_title_duplication(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t1 = model.Goal("b1012100", "test title")
        t1.insert(db)
        self.assertTrue(t1.serial is not None)
        t2 = model.Goal("b1012100", "test title")
        with self.assertRaises(model.GoalTitleDuplicated):
            t2.insert(db)

    def test_find(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        t1 = model.Goal("b1012100", "test title")
        t2 = model.Goal("b1012100", "test title1")
        t1.insert(db)
        self.assertTrue(t1.serial is not None)
        t2.insert(db)
        self.assertTrue(t2.serial is not None)
        self.assertNotEqual(t1.serial, t2.serial)
        act1 = model.Goal.find(db, "b1012100", t1.serial)
        act2 = model.Goal.find(db, "b1012100", t2.serial)
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None)
        self.assertEqual(act1.serial, t1.serial)
        self.assertEqual(act2.serial, t2.serial)

    def test_get(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        g1 = model.Goal("b1012100", "text title")
        g1.insert(db)
        self.assertTrue(g1.serial is not None)
        act = model.Goal.get(db, "b1012100")
        self.assertTrue(act != None)
        for goal in act:
            self.assertTrue(goal.student_id == "b1012100")
            self.assertEqual(goal.serial, g1.serial)

    def test_get_false(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        g1 = model.Goal("b1012100", "text title")
        g1.insert(db)
        self.assertTrue(g1.serial is not None)
        act = model.Goal.get(db, "b1012101")
        self.assertEqual(act, [])

    def test_remove(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        r1 = model.Goal("b1012100", "test title")
        r1.insert(db)
        self.assertTrue(r1.serial is not None)
        model.Goal.remove(db, "b1012100", r1.serial)
        act = model.Goal.find(db, "b1012100", r1.serial)
        self.assertTrue(act == None)

    def test_remove_false(self):
        db = Connection('localhost', 27017).testdata
        model.Goal.delete_all(db)
        r1 = model.Goal("b1012100", "test title")
        r1.insert(db)
        self.assertTrue(r1.serial is not None)
        model.Goal.remove(db, "b1012101", r1.serial)
        model.Goal.remove(db, "b1012100", r1.serial + 1)
        act = model.Goal.find(db, "b1012100", r1.serial)
        self.assertTrue(act != None)


class GoalItemTest(unittest.TestCase):
    def test_init(self):
        goal_serial = 1
        i1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)

    def test_insert(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        i1.insert(db)
        self.assertTrue(i1.serial is not None)

    def test_insert_duplication(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        i1.insert(db)
        self.assertTrue(i1.serial is not None)
        with self.assertRaises(model.GoalItemInsertedTwice):
            i1.insert(db)


    def test_insert_title_duplication(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        i1.insert(db)
        self.assertTrue(i1.serial is not None)
        i2 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        with self.assertRaises(model.GoalItemTitleDuplicated):
            i2.insert(db)


    def test_find(self):
        goal_serial1 = 1
        goal_serial2 = 2
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        i1 = model.GoalItem("b1012100", goal_serial1, "test title", "testdata", False)
        i2 = model.GoalItem("b1012100", goal_serial2, "test title1", "testdata1", False)
        i1.insert(db)
        self.assertTrue(i1.serial is not None)
        i2.insert(db)
        self.assertTrue(i2.serial is not None)
        act1 = model.GoalItem.find(db, "b1012100", i1.serial)
        act2 = model.GoalItem.find(db, "b1012100", i2.serial)
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None)

    def test_get(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        g1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        g1.insert(db)
        self.assertTrue(g1.serial is not None)
        act = model.GoalItem.get(db, "b1012100", goal_serial)
        self.assertTrue(act != None)
        for goal in act:
            self.assertTrue(goal.student_id == "b1012100")

    def test_get_false(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        g1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        g1.insert(db)
        self.assertTrue(g1.serial is not None)
        act1 = model.GoalItem.get(db, "b1012101", goal_serial)
        self.assertEqual(act1, [])

    def test_remove(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        r1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        r1.insert(db)
        self.assertTrue(r1.serial is not None)
        model.GoalItem.remove(db, "b1012100", r1.serial)
        act = model.GoalItem.find(db, "b1012100", r1.serial)
        self.assertTrue(act == None)

    def test_remove_false(self):
        goal_serial = 1
        db = Connection('localhost', 27017).testdata
        model.GoalItem.delete_all(db)
        r1 = model.GoalItem("b1012100", goal_serial, "test title", "testdata", False)
        r1.insert(db)
        model.GoalItem.remove(db, "b1012101", r1.serial)
        model.GoalItem.remove(db, "b1012100", r1.serial + 1)
        act = model.GoalItem.find(db, "b1012100", r1.serial)
        self.assertTrue(act != None)


class ItemLogTest(unittest.TestCase):
    def test_init(self):
        goalitem_serial = 1
        i1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")

    def test_insert(self):
        goalitem_serial = 1
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        i1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")
        i1.insert(db)
        self.assertTrue(i1.serial is not None)

    def test_find(self):
        goalitem_serial = 1
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        i1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")
        i2 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge1")
        i1.insert(db)
        self.assertTrue(i1.serial is not None)
        i2.insert(db)
        self.assertTrue(i2.serial is not None)
        self.assertNotEqual(i1.serial, i2.serial)
        act1 = model.ItemLog.find(db, "b1012100", i1.serial)
        act2 = model.ItemLog.find(db, "b1012100", i2.serial)
        self.assertTrue(act1 != None)
        self.assertTrue(act2 != None) 

    def test_get(self):
        goalitem_serial = 1
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        i1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")
        i1.insert(db)
        act = model.ItemLog.get(db, "b1012100")
        self.assertTrue(act != None)
        for itemlog in act:
            self.assertTrue(itemlog.student_id == "b1012100")

    def test_get_false(self):
        goalitem_serial = 1
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        i1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")
        i1.insert(db)
        act = model.ItemLog.get(db, "b1012101")
        self.assertTrue(act == None)

    def test_remove(self):
        goalitem_serial = 1
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        r1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")
        number1 = r1.insert(db)
        model.ItemLog.remove(db, "b1012100", number1)
        act = model.ItemLog.find(db, "b1012100", number1)
        self.assertTrue(act == None)

    def test_remove_false(self):
        goalitem_serial = 1
        db = Connection('localhost', 27017).testdata
        model.ItemLog.delete_all(db)
        r1 = model.ItemLog("b1012100", goalitem_serial, "2013/11/11", "hogehoge")
        r1.insert(db)
        model.ItemLog.remove(db, "b1012101", r1.serial)
        model.ItemLog.remove(db, "b1012100", r1.serial + 1)
        act = model.ItemLog.find(db, "b1012100", r1.serial)
        self.assertTrue(act != None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
