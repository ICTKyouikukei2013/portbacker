# -*- coding:utf-8 -*-

import urllib
import sys, os, datetime, itertools
from flask import Flask, session, request, redirect, url_for, render_template , send_from_directory, escape
from pymongo import Connection
from werkzeug import secure_filename

UPLOAD_FOLDER = u'./data'
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

def render_template_with_username(url,**keywordargs):
    username = session.get('username')
    return render_template(url,username=username,**keywordargs)

@app.before_request
def befor_request():
    if session.get('username') is not None:
        return
    if request.path == '/login':
        return
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username') is not None:
        return redirect('/')
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if its there
    session.pop('username', None)
    return redirect('/login')

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploaded_file')
def uploaded_file():
    return 'success upload %s!' % request.args["filename"]

@app.route('/', methods=['GET'])
def index_page():
    return render_template_with_username("top.html")

# goal.htmlにリンク
@app.route('/goal', methods=['GET'])
def goal_get():
    username = session['username']
    col = db.goals
    docs = col.find({"username": username})
    return render_template_with_username("goal.html", docs=docs)

# goal_textの内容を受け取ってgoal.htmlに渡す 菅野：テキストは渡さないでgoal.htmlからdbにアクセスできるようにしました
@app.route('/goal', methods=['POST'])
def goal_post():
    username = session['username']
    col = db.goals
    if request.form["button"] == u"新規作成":
        goal_text = request.form['goal_text']
        if goal_text != "":
            col.insert({"username": username, "goal_text": goal_text})
    elif request.form["button"] == u"削除":
        rmgoal = request.form['rmgoal']
        col.remove({"username": username, "goal_text": rmgoal})
    docs = col.find({"username": username})
    return render_template_with_username("goal.html", docs=docs)

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

    return render_template_with_username("portfolio.html", zipped=zipped)

def get_date(filename):
    stat = os.stat(os.path.join(UPLOAD_FOLDER, filename))
    last_modified = stat.st_mtime
    dt = datetime.datetime.fromtimestamp(last_modified)
    return dt.strftime("%Y/%m/%d")

def unquote(s):
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return urllib.unquote(s).decode('utf-8')

def quote(s):
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return urllib.quote(s)

def list_files_and_dirs(dirpath):
    filelist = os.listdir(dirpath)
    dirlist = []  # list of (display, url)
    filelist2 = []  # list of (display, url)
    def to_display_and_url(name):
        return (name, quote('utf-8'))
    for name in filelist:
        if os.path.isdir(os.path.join(dirpath, name)):
            dirlist.append((name, quote(name)))
        else:
            filelist2.append((name, quote(name)))
    return filelist2, dirlist

def check_filename(filename):
    unpermitted_chars = '&:;"' + "'"
    for c in unpermitted_chars:
        if c in filename:
            return False
    for c in filename:
        if ord(c) < 0x20:  # ctrl chars
            return False
    return True

@app.route('/artifact/<path:dirpath>', methods=['GET', 'POST'])
def artifact_dir(dirpath):
    if request.method == 'POST':
        makedir = unquote(request.form['directoryname'])
        file = request.files['file']
        if file:
            if allowed_file(file.filename) and check_filename(file.filename):
                file.save(os.path.join(UPLOAD_FOLDER, dirpath, file.filename))
            else:
                sys.stderr.write("log> upload failed (unallowed name): %s\n" % repr(file.filename))
        elif makedir:
            os.mkdir(os.path.join(UPLOAD_FOLDER, dirpath, makedir))

    filelist2, dirlist = list_files_and_dirs(os.path.join(UPLOAD_FOLDER, dirpath))
    return render_template_with_username("artifact.html",ls=filelist2,dir=dirlist,
            dirpath=quote(dirpath) + "/")

@app.route('/artifact', methods=['GET', 'POST'])
def artifact():
    if request.method == 'POST':
        makedir = unquote(request.form['directoryname'])
        file = request.files['file']
        if file:
            if allowed_file(file.filename) and check_filename(file.filename):
                file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            else:
                sys.stderr.write("log> upload failed (unallowed name): %s\n" % repr(file.filename))
        elif makedir:
            os.mkdir(os.path.join(UPLOAD_FOLDER, makedir))

    filelist2, dirlist = list_files_and_dirs(UPLOAD_FOLDER)
    return render_template_with_username("artifact.html",ls=filelist2,dir=dirlist,dirpath="")

@app.route('/view_file/<path:filename>')
def view_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# portfolioの新規作成ページ
@app.route('/new', methods=['GET'])
def new():
    filelist = os.listdir(UPLOAD_FOLDER)
    imglist = []
    artifact_list = []
    for filename in filelist:
        if '.' in filename and filename.rsplit('.', 1)[1] in IMAGE_EXTENSIONS:
            imglist.append(filename)
        else:
            artifact_list.append(filename)

    return render_template_with_username("new.html", imglist=imglist, artifact_list=artifact_list)

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

if __name__ == '__main__':
    app.debug = True
    app.run()
