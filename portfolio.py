# -*- coding:utf-8 -*-

import sys, os, datetime, itertools
from flask import Flask, request, redirect, url_for, render_template , send_from_directory
from pymongo import Connection
from werkzeug import secure_filename

UPLOAD_FOLDER = './data'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

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
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploaded_file')
def uploaded_file():
    return 'success upload %s!' % request.args["filename"]

@app.route('/', methods=['GET'])
def index_page():
    return render_template("top.html")

# goal.htmlにリンク
@app.route('/goal', methods=['GET'])
def goal_get():
    col = db.portfolios
    return render_template("goal.html", col=col)

# goal_textの内容を受け取ってgoal.htmlに渡す 菅野：テキストは渡さないでgoal.htmlからdbにアクセスできるようにしました
@app.route('/goal', methods=['POST'])
def goal_post():
    col = db.portfolios
    if request.form["button"] == u"設定":
        goal_text = request.form['goal_text']
        col.insert({"goal_text":goal_text})
    elif request.form["button"] == u"削除":
        rmgoal = request.form['rmgoal']
        col.remove({"goal_text":rmgoal})
    return render_template("goal.html", col=col)

@app.route('/portfolio')
def portfolio():
    portlists = []
    datelist = []
    portfolio_filelist = []
    filelist = os.listdir(UPLOAD_FOLDER)
    for filename in filelist:
        if 'portfolio' in filename and '.html' in filename:
            portfolio_filelist.append(filename)
    
    portfolio_filelist.sort(key=get_date, reverse=True)

    for k, g in itertools.groupby(portfolio_filelist, key=get_date):
        portlists.append(list(g))      # Store group iterator as a list
        datelist.append(k)

    zipped = zip(datelist, portlists)

    return render_template("portfolio.html", zipped=zipped)

def get_date(filename):
    stat = os.stat(UPLOAD_FOLDER + "/" + filename)
    last_modified = stat.st_mtime
    dt = datetime.datetime.fromtimestamp(last_modified)
    return dt.strftime("%Y/%m/%d")

@app.route('/artifact/<path:dirpath>', methods=['GET', 'POST'])
def artifact_dir(dirpath):
    if request.method == 'POST':
        makedir = request.form['directoryname']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER+"/"+dirpath, filename))
        elif makedir:
            os.mkdir(UPLOAD_FOLDER+"/"+dirpath+"/"+makedir)

    filelist = os.listdir(UPLOAD_FOLDER+"/"+dirpath)
    dirlist = []
    filelist2 = []
    for name in filelist:
        if os.path.isdir(UPLOAD_FOLDER+"/"+dirpath+"/"+name):
            dirlist.append(name)
        else:
            filelist2.append(name)
    return render_template("artifact.html",ls=filelist2,dir=dirlist,dirpath=dirpath+"/")

@app.route('/artifact', methods=['GET', 'POST'])
def artifact():
    if request.method == 'POST':
        makedir = request.form['directoryname']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif makedir:
            os.mkdir("./data/"+makedir)

    filelist = os.listdir(UPLOAD_FOLDER)
    dirlist = []
    filelist2 = []
    for name in filelist:
        if os.path.isdir("./data/"+name):
            dirlist.append(name)
        else:
            filelist2.append(name)
    return render_template("artifact.html",ls=filelist2,dir=dirlist,dirpath="")


@app.route('/view_file/<path:filename>')
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

@app.route('/mongo', methods=['GET'])
def mongo_get():
    # testデータベースからfooコレクションを取得
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

# portfolioの新規作成ページ
@app.route('/new', methods=['GET'])
def new():
    filelist = os.listdir(UPLOAD_FOLDER)
    imglist = []
    for filename in filelist:
        if '.' in filename and filename.rsplit('.', 1)[1] in IMAGE_EXTENSIONS:
            imglist.append(filename)

    return render_template("new.html", imglist=imglist)

@app.route('/new', methods=['POST'])
def new_post():
    filelist = os.listdir(UPLOAD_FOLDER)
    filelist.sort()
    nonexist_i = None
    for i in range(1, 100):
        if ("portfolio%d.html" % i) not in filelist:
            nonexist_i = i
            break
    else:
        assert False, "too many portfolios"
    i = nonexist_i
    with open(os.path.join(UPLOAD_FOLDER, "portfolio%d.html" % i), "wb") as f:
        text = request.form["textarea"].encode('utf-8')
        f.write(text)
    return portfolio()

@app.route('/preview', methods=['POST'])
def preview():
    return request.form['textarea']


# print "========find_one========"
# print col.find_one()

# print "========find========"
# for data in col.find():
#     print data

if __name__ == '__main__':
    app.debug = True
    app.run()
