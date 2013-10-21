#coding: utf-8

from pymongo import Connection

class User(object):
    def __init__(self, name, student_id, joining_groups, course, grade):
        self.name = name
        self.student_id = student_id
        self.joining_groups = joining_groups
        self.course = course
        self.grade = grade

    def insert(self, db):
        col = db.portfolio_users
        col.insert({
            "name": self.name,
            "student_id":self.student_id,
            "joining_groups":self.joining_groups,
            "course":self.course,
            "grade":self.grade})

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

db = Connection('localhost', 27017).portbacker

COL_GOALS = "goals"
COL_PERSONALLOGS = "personallogs"

def get_text_by_user_table_coumn(username, table, column):
    col = db[table]
    docs = col.find({"username": username})
    texts = [doc.get(column) for doc in docs]
    texts = list(filter(None, texts))
    return texts

def get_goal_texts(username):
    goal_texts = get_text_by_user_table_coumn(username, COL_GOALS, "goal_text")
    return goal_texts

def remove_goal_text(username, goal_text):
    col = db[COL_GOALS]
    col.remove({"username": username, "goal_text": goal_text})

def insert_goal_text(username, goal_text):
    col = db[COL_GOALS]
    col.insert({"username": username, "goal_text": goal_text})

def get_log_texts(username):
    log_texts = get_text_by_user_table_coumn(username, COL_PERSONALLOGS, "personallog_text")
    return log_texts

def remove_log_text(username, log_text):
    col = db[COL_PERSONALLOGS]
    col.remove({"username": username, "personallog_text": log_text})

def insert_log_text(username, log_text):
    col = db[COL_PERSONALLOGS]
    col.insert({"username": username, "personallog_text": log_text})

