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

class GoalDuplicationError(ValueError):
    pass

class Goal(object):
    def __init__(self, student_id, title):
        self.student_id = student_id
        self.title = title
        
    def insert(self, db):
        col = db.portfolio_goals
        if Goal.find(db, self.student_id, self.title) != None:
            raise GoalDuplicationError()
        col.insert({
            "student_id": self.student_id,
            "title": self.title})
            
    @classmethod
    def find(clz , db, student_id, title):
        col = db.portfolio_goals
        docs = col.find({"student_id": student_id, "title": title})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return Goal(doc["student_id"], doc["title"])

    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_goals")
    
    @classmethod
    def get(clz, db, student_id):
        col = db.portfolio_goals
        docs = col.find({"student_id": student_id})
        docs = list(docs)
        if len(docs) == 0:
            return None
        else :
            return [Goal(doc["student_id"], doc["title"]) for doc in docs] 

    @classmethod
    def remove(clz, db, student_id, title):
        col = db.portfolio_goals
        col.remove({"student_id": student_id, "title": title})


class GoalItemDuplicationError(ValueError):
    pass

class GoalItem(object):
    def __init__(self, student_id, link_to_goal, title, change_data, visibility):
        self.student_id = student_id
        self.link_to_goal = link_to_goal
        self.title = title
        self.change_data = change_data 
        self.visibility = visibility 
    
    def insert(self, db):
        col = db.portfolio_goal_items
        if GoalItem.find(db, self.student_id,self.link_to_goal, self.title) != None:
            raise GoalItemDuplicationError()
        col.insert({
            "student_id": self.student_id,
            "link_to_goal": self.link_to_goal,
            "title": self.title,
            "change_data": self.change_data,
            "visibility": self.visibility})
    
    @classmethod 
    def find(clz , db, student_id, link_to_goal, title):
        col = db.portfolio_goal_items
        docs = col.find({
            "student_id": student_id, 
            "link_to_goal": link_to_goal,
            "title": title})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return GoalItem(doc["student_id"], doc["link_to_goal"], doc["title"], doc["change_data"], doc["visibility"])
    
    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_goal_items")


class ItemLog(object):
    def __init__(self, student_id, link_to_goal, link_to_goal_item, creation_date, text, number=None ):
        self.student_id = student_id
        self.link_to_goal = link_to_goal
        self.link_to_goal_item = link_to_goal_item
        self.creation_date = creation_date 
        self.text = text 
        if number != None:
            self.number = number
        else :
            self.number = None 


    def insert(self, db):
        col = db.portfolio_item_logs
        if self.number != None:
            number = self.number
        else :
            docs = col.find({
               "student_id" : self.student_id})
            docs = list(docs)
            max_number = 0
            for doc in docs:
                max_number = max(max_number, doc["number"])
            number = max_number+1
            
        col.insert({
            "student_id": self.student_id,
            "link_to_goal": self.link_to_goal,
            "link_to_goal_item": self.link_to_goal_item,
            "number": number,
            "creation_date" : self.creation_date,
            "text" : self.text })
        return number

    @classmethod
    def find(clz, db, student_id, number):
        col = db.portfolio_item_logs
        docs = col.find({
            "student_id" : student_id,
            "number" : number})
        docs = list(docs)
        if len(docs) == 0:
            return None
        doc = docs[0]
        return ItemLog(doc["student_id"], doc["link_to_goal"], doc["link_to_goal_item"], doc["number"], doc["creation_date"], doc["text"])

    @classmethod
    def get(clz, db, student_id):
        col = db.portfolio_item_logs
        docs = col.find({"student_id": student_id})
        docs = list(docs)
        if len(docs) == 0:
            return None
        else :
            return [ItemLog(doc["student_id"], doc["link_to_goal"], doc["link_to_goal_item"], doc["number"], doc["creation_date"], doc["text"]) for doc in docs] 

    @classmethod
    def remove(clz, db, student_id, number):
        col = db.portfolio_item_logs
        col.remove({"student_id": student_id, "number": number})

    @classmethod
    def delete_all(clz, db):
        db.drop_collection("portfolio_item_logs")    
    

db = Connection('localhost', 27017).portbacker

COL_GOALS = "goals"
COL_PERSONALLOGS = "personallogs"

def get_text_by_user_table_coumn(student_id, table, column):
    col = db[table]
    docs = col.find({"student_id": student_id})
    texts = [doc.get(column) for doc in docs]
    texts = list(filter(None, texts))
    return texts

def get_goal_texts(student_id):
    goal_texts = get_text_by_user_table_coumn(student_id, COL_GOALS, "goal_text")
    return goal_texts

def remove_goal_text(student_id, goal_text):
    col = db[COL_GOALS]
    col.remove({"student_id": student_id, "goal_text": goal_text})

def insert_goal_text(student_id, goal_text):
    col = db[COL_GOALS]
    col.insert({"student_id": student_id, "goal_text": goal_text})

def get_log_texts(student_id):
    log_texts = get_text_by_user_table_coumn(student_id, COL_PERSONALLOGS, "personallog_text")
    return log_texts

def remove_log_text(student_id, log_text):
    col = db[COL_PERSONALLOGS]
    col.remove({"student_id": student_id, "personallog_text": log_text})

def insert_log_text(student_id, log_text):
    col = db[COL_PERSONALLOGS]
    col.insert({"student_id": student_id, "personallog_text": log_text})
