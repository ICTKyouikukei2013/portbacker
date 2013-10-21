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
		if len(docs) == 0;
			return None
		doc = docs[0]
		return Group(doc["name"], doc["gruop_id"])
		
	@classmethod
	def delete_all(clz, db):
		db.portfolio.gruops_drop()

class User(object):
    def __init__(self, display_name, student_id, group_id, course, grade):
        self.display_name = display_name
        self.student_id = student_id
        self.group_id = group_id
        self.course = course
        self.grade = grade

    def insert(self, db):
        col = db.portpolio_users
        col.insert({
            "display_name": self.display_name,
            "student_id":self.student_id,
            "group_id":self.group_id,
            "course":self.course,
            "grade":self.grade})

    @classmethod
    def find(clz, db, student_id):
        col = db.portpolio_users
        docs = col.find({"student_id": student_id})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return User(doc["display_name"], doc["student_id"], doc["group_id"], doc["course"], doc["grade"])

    @classmethod
    def find_user_ids(clz, db):
        col = db.portpolio_users
        docs = col.find()
        store = []
        for doc in docs:
            store.append(doc["student_id"])
        return store

    @classmethod
    def delete_all(clz, db):
        db.portpolio_users.drop()

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

