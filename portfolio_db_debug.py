#coding: utf-8

from portfolio import app, db
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

db_debug_page = Blueprint('db_debug_page', __name__)

@db_debug_page.route('/mongo', methods=['GET'])
def mongo_get():
    # testデータベースからfooコレクションを取得
    return render_template("mongo.html", db=db)

@db_debug_page.route('/mongo', methods=['POST'])
def mongo_post():
    col = db.portfolios
    if request.form['button'] == u"設定":
        public = request.form['public'] == "true"
        owner = request.form['owner']
        text = request.form['text']

        col.insert({"public":public, "owner":owner, "text":text})
    else:
        col.remove({"owner":request.form['owner']})
    
    return render_template("mongo_post.html")

app.register_blueprint(db_debug_page)

# print "========find_one========"
# print col.find_one()

# print "========find========"
# for data in col.find():
#     print data

if __name__ == '__main__':
    app.debug = True
    app.run()
