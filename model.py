#coding: utf-8

from pymongo import Connection

class Group(object):
    def __init__(self, name, group_id):
        self.name = name
        self.group_id = group_id
        
    def insert(self, db):
        col = db.portfolio_groups
        col.insert({
            "name": self.name,
            "group_id": self.group_id})
            
    @classmethod
    def find(clz , db, group_id):
        col = db.portfolio_groups
        docs = col.find({"group_id": group_id})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return Group(doc["name"], doc["group_id"])
        
    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_groups")

def delete_all_serial_numbers(db):
    db.drop_collection("serial_number")

def gen_serial_number(student_id, db):
    col = db.serial_number
    docs = col.find({"student_id": student_id})
    docs = list(docs)
    if not docs:
        col.insert({"student_id": student_id, "seq": 0})
    return col.find_and_modify({"student_id": student_id}, update={"$inc": {"seq": 1}}, new=True)["seq"]

class UserDuplicationError(ValueError):
    pass

class User(object):
    def __init__(self, name, student_id, joining_groups, course, grade):
        self.name = name
        self.student_id = student_id
        self.joining_groups = joining_groups
        self.course = course
        self.grade = grade

    def insert(self, db):
        col = db.portfolio_users
        if User.find(db, self.student_id) != None:
            raise UserDuplicationError
        col.insert({
            "name": self.name,
            "student_id":self.student_id,
            "joining_groups":self.joining_groups,
            "course":self.course,
            "grade":self.grade})

    def update(self, db):
        col = db.portfolio_users
        col.update({"student_id": self.student_id}, {"name":self.name, "student_id":self.student_id, "joining_groups": self.joining_groups, "course": self.course, "grade": self.grade})

    @classmethod
    def find(clz, db, student_id):
        col = db.portfolio_users
        docs = col.find({"student_id": student_id})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return User(doc["name"], doc["student_id"], doc["joining_groups"], doc["course"], doc["grade"])

    @classmethod
    def find_user_ids(clz, db):
        col = db.portfolio_users
        docs = col.find()
        store = []
        for doc in docs:
            store.append(doc["student_id"])
        return store

    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_users")
        delete_all_serial_numbers(db)

    @classmethod
    def find_user_ids_by_joining_group(clz, db, group_id):
        col = db.portfolio_users
        docs = col.find()
        store = []
        for doc in docs:
            joining_groups = doc["joining_groups"]
            if group_id in joining_groups:
                store.append(doc["student_id"])
        return store

class GoalInsertedTwice(ValueError):
    pass

class GoalTitleDuplicated(ValueError):
    pass

class Goal(object):
    def __init__(self, student_id, title, serial=None):
        self.student_id = student_id
        self.title = title
        self.serial = serial

    def insert(self, db):
        if self.serial is not None:
            raise GoalInsertedTwice
        serial = gen_serial_number(self.student_id, db)
        col = db.portfolio_goals

        docs = col.find({
            "student_id": self.student_id,
            "title": self.title})
        docs = list(docs)
        if docs:
            raise GoalTitleDuplicated

        col.insert({
            "student_id": self.student_id,
            "title": self.title,
            "serial": serial})

        # if insertion failed, will not reach here
        self.serial = serial

    @classmethod
    def find(clz, db, student_id, serial):  # TODO API changed
        col = db.portfolio_goals
        docs = col.find({"student_id": student_id, "serial": serial})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return Goal(doc["student_id"], doc["title"], doc["serial"])

    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_goals")

    @classmethod
    def get(clz, db, student_id):
        col = db.portfolio_goals
        docs = col.find({"student_id": student_id})
        docs = list(docs)
        return [Goal(doc["student_id"], doc["title"], doc["serial"]) for doc in docs] 

    @classmethod
    def remove(clz, db, student_id, serial):  # TODO API changed
        col = db.portfolio_goals
        col.remove({"student_id": student_id, "serial": serial})

class GoalItemInsertedTwice(ValueError):
    pass

class GoalItemTitleDuplicated(ValueError):
    pass

class GoalItem(object):
    def __init__(self, student_id, goal_serial, title, change_data, visibility, serial=None):  # TODO API changed
        self.student_id = student_id
        self.goal_serial = goal_serial
        self.title = title
        self.change_data = change_data 
        self.visibility = visibility
        self.serial = serial

    def insert(self, db):
        if self.serial is not None:
            raise GoalItemInsertedTwice
        serial = gen_serial_number(self.student_id, db)
        col = db.portfolio_goal_items

        docs = col.find({
            "student_id": self.student_id,
            "goal_serial": self.goal_serial,
            "title": self.title})
        docs = list(docs)
        if docs:
            raise GoalItemTitleDuplicated

        col.insert({
            "student_id": self.student_id,
            "goal_serial": self.goal_serial,
            "title": self.title,
            "change_data": self.change_data,
            "visibility": self.visibility,
            "serial": serial})

        # if insertion failed, will not reach here
        self.serial = serial

    def update(self, db):
        assert self.serial  # has been inserted?
        GoalItem.remove(db, self.student_id, self.goal_serial)
        col = db.portfolio_goal_items
        col.insert({
            "student_id": self.student_id,
            "goal_serial": self.goal_serial,
            "title": self.title,
            "change_data": self.change_data,
            "visibility": self.visibility,
            "serial": self.serial})

    @classmethod 
    def find(clz, db, student_id, serial):  # TODO API changed
        col = db.portfolio_goal_items
        docs = col.find({
            "student_id": student_id, 
            "serial": serial})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return GoalItem(doc["student_id"], doc["goal_serial"], doc["title"], doc["change_data"], doc["visibility"], doc["serial"])

    @classmethod 
    def get(clz , db, student_id, goal_serial):
        col = db.portfolio_goal_items
        docs = col.find({
            "student_id": student_id, 
            "goal_serial": goal_serial})
        docs = list(docs)
        return [GoalItem(doc["student_id"], doc["goal_serial"], doc["title"], doc["change_data"], doc["visibility"], doc["serial"]) for doc in docs]

    @classmethod
    def remove(clz, db, student_id, serial):  # TODO API changed
        col = db.portfolio_goal_items
        col.remove({"student_id": student_id, "serial": serial})

    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_goal_items")

class ItemLogInsertedTwice(ValueError):
    pass

class ItemLog(object):
    def __init__(self, student_id, goalitem_serial, creation_date, text, serial=None):  # TODO API changed
        self.student_id = student_id
        self.goalitem_serial = goalitem_serial
        self.creation_date = creation_date 
        self.text = text 
        self.serial = serial

    def insert(self, db):  # TODO API changed
        if self.serial is not None:
            raise ItemLogInsertedTwice
        serial = gen_serial_number(self.student_id, db)
        col = db.portfolio_item_logs
        col.insert({
            "student_id": self.student_id,
            "goalitem_serial": self.goalitem_serial,
            "creation_date": self.creation_date,
            "text": self.text,
            "serial": serial })

        # if insertion failed, will not reach here
        self.serial = serial

    @classmethod
    def find(clz, db, student_id, serial):  # TODO API changed
        col = db.portfolio_item_logs
        docs = col.find({
            "student_id" : student_id,
            "serial" : serial})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return ItemLog(doc["student_id"], doc["goalitem_serial"], doc["creation_date"], doc["text"], doc["serial"])

    @classmethod
    def get(clz, db, student_id):
        col = db.portfolio_item_logs
        docs = col.find({"student_id": student_id})
        docs = list(docs)
        if len(docs) == 0:
            return None
        else:
            return [ItemLog(doc["student_id"], doc["goalitem_serial"], doc["creation_date"], doc["text"], doc["serial"]) for doc in docs] 

    @classmethod
    def remove(clz, db, student_id, serial):  # TODO API changed
        col = db.portfolio_item_logs
        col.remove({"student_id": student_id, "serial": serial})

    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_item_logs")    
    

db = Connection('localhost', 27017).portbacker

# COL_GOALS = "goals"
# COL_PERSONALLOGS = "personallogs"
# 
# def get_text_by_user_table_coumn(student_id, table, column):
#     col = db[table]
#     docs = col.find({"student_id": student_id})
#     texts = [doc.get(column) for doc in docs]
#     texts = list(filter(None, texts))
#     return texts
# 
# def get_goal_texts(student_id):
#     goal_texts = get_text_by_user_table_coumn(student_id, COL_GOALS, "goal_text")
#     return goal_texts
# 
# def remove_goal_text(student_id, goal_text):
#     col = db[COL_GOALS]
#     col.remove({"student_id": student_id, "goal_text": goal_text})
# 
# def insert_goal_text(student_id, goal_text):
#     col = db[COL_GOALS]
#     col.insert({"student_id": student_id, "goal_text": goal_text})
# 
# def get_log_texts(student_id):
#     log_texts = get_text_by_user_table_coumn(student_id, COL_PERSONALLOGS, "personallog_text")
#     return log_texts
# 
# def remove_log_text(student_id, log_text):
#     col = db[COL_PERSONALLOGS]
#     col.remove({"student_id": student_id, "personallog_text": log_text})
# 
# def insert_log_text(student_id, log_text):
#     col = db[COL_PERSONALLOGS]
#     col.insert({"student_id": student_id, "personallog_text": log_text})
