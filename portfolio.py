# -*- coding:utf-8 -*-

import sys, os
from flask import Flask, request, redirect, url_for, render_template
from pymongo import Connection
from werkzeug import secure_filename

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# コネクション作成
con = Connection('localhost', 27017)

# コネクションからtestデータベースを取得
db = con.portbacker

# 以下のように記載することも可能
# db = con['test']

# testデータベースからfooコレクションを取得
# col = db.portfolios

# 以下のように記載することも可能
# col = db['foo']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploaded_file')
def uploaded_file():
  return 'success upload %s!' % request.args["filename"]

@app.route('/', methods=['GET'])
def index_page():
    return render_template("top.html")

# goal.htmlにリンク
@app.route('/goal', methods=['GET'])
def goal_get():
    return render_template("goal.html")

# goal_textの内容を受け取ってgoal.htmlに渡す
@app.route('/goal', methods=['POST'])
def goal_post():
    goal_text = request.form['goal_text']
    return render_template("goal.html", goal_text=goal_text)

@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")

@app.route('/artifact', methods=['GET', 'POST'])
def artifact():
    if request.method == 'POST':
 
        file = request.files['file']
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                return render_template("upload_error.html", filename=file.filename)
    filelist = os.listdir(UPLOAD_FOLDER)
    return render_template("artifact.html",ls=filelist)

@app.route('/mongo', methods=['GET'])
def mongo_get():
    # testデータベースからfooコレクションを取得
    col = db.portfolios

    return render_template("mongo.html", db=db)

@app.route('/mongo', methods=['POST'])
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

# print "========find_one========"
# print col.find_one()

# print "========find========"
# for data in col.find():
#     print data

if __name__ == '__main__':
    app.debug = True
    app.run()
