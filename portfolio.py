# -*- coding:utf-8 -*-

import urllib
import sys, os, datetime, itertools
from flask import Flask, session, request, redirect, url_for, render_template , send_from_directory, escape
#gfrom werkzeug import secure_filename
import model

UPLOAD_FOLDER = u'./data'
DOCUMENT_EXTENSIONS = frozenset(['txt', 'pdf', 'md'])
IMAGE_EXTENSIONS = frozenset(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS = DOCUMENT_EXTENSIONS.union(IMAGE_EXTENSIONS)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def render_template_with_username(url,**keywordargs):
    username = session.get('username')
    return render_template(url,username=username,**keywordargs)

def instance_of_ldap(username, password):
    return True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_date(filename):
    stat = os.stat(path_from_sessionuser_root(filename))
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
    dirs_and_files = os.listdir(dirpath)
    dirlist = []
    filelist = []
    for name in dirs_and_files:
        (dirlist if os.path.isdir(os.path.join(dirpath, name)) else filelist) \
        .append(name)
    return filelist, dirlist

def check_filename(filename):
    unpermitted_chars = '&:;"' + "'"
    if any((c in filename) for c in unpermitted_chars):
        return False
    if any((ord(c) < 0x20) for c in filename):  # including control chars?
        return False
    return True

def path_from_sessionuser_root(*p):
    s = [UPLOAD_FOLDER, session['username']]
    s.extend(p)
    return os.path.join(*s)

@app.before_request
def befor_request():
    if session.get('username') is not None:
        return
    if request.path == '/login':
        return
    if 'static' in request.path.split('/'):
        return
    return redirect('/login')

@app.route('/login', methods=['GET'])
def login_get():
    if session.get('username') is not None:
        return redirect('/')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    if not instance_of_ldap(username, password):
        return redirect('/login')
    session['username'] = username
    if not os.path.isdir(os.path.join(UPLOAD_FOLDER, username)):
        os.mkdir(path_from_sessionuser_root())
    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    # remove the username from the session if its there
    session.pop('username', None)
    return redirect('/login')

@app.route('/uploaded_file', methods=['GET'])
def uploaded_file():
    return 'success upload %s!' % request.args["filename"]

@app.route('/', methods=['GET'])
def index_page():
    return render_template_with_username("top.html")

# goal.htmlにリンク
@app.route('/goal', methods=['GET'])
def get_goal():
    username = session['username']
    goal_texts = model.get_goal_texts(username)
    log_texts = model.get_log_texts(username)
    return render_template_with_username("goal.html", goal_texts= goal_texts, log_texts=log_texts)

# goal_textの内容を受け取ってgoal.htmlに渡す 菅野：テキストは渡さないでgoal.htmlからdbにアクセスできるようにしました
@app.route('/goal_post_goal', methods=['POST'])
def post_goal():
    username = session['username']
    if request.form["button_name"] == "make":
        goal_title = request.form['goal_title']
        g = model.Goal(goal_title)
        g.insert(model.db)
    return redirect('/goal')

@app.route('/goal_post_goal_item', methods=['POST'])
def post_goal_item():
    username = session['username']
    if request.form["button_name"] == "make":
        goal_item_text = request.form["goal_item_title"]
        goal_title = request.form['goal_title']
        gi = model.Goal_item(goal_item_title, get_date(), goal_title, True)
    return redirect('/goal')

@app.route('/personallog_post', methods=['POST'])
def personallog_post():
    username = session['username']
    if request.form["button"] == u"追加":
        personallog_text = request.form['personallog_text']
        if personallog_text != "":
            model.insert_log_text(username, personallog_text)
    elif request.form["button"] == u"削除":
        rmlog = request.form['rmgoal']
        model.remove_log_text(username, rmlog)
    goal_texts = model.get_goal_texts(username)
    log_texts = model.get_log_texts(username)
    return render_template_with_username("goal.html", 
            goal_texts=goal_texts, log_texts=log_texts)

@app.route('/portfolio', methods=['GET'])
def portfolio():
    portlists = []
    datelist = []
    portfolio_filelist = []
    filelist = os.listdir(path_from_sessionuser_root())
    for filename in filelist:
        if 'portfolio' in filename and '.html' in filename:
            portfolio_filelist.append(filename)
    
    portfolio_filelist.sort(key=get_date, reverse=True)

    for k, g in itertools.groupby(portfolio_filelist, key=get_date):
        portlists.append(list(g))      # Store group iterator as a list
        datelist.append(k)

    zipped = zip(datelist, portlists)

    return render_template_with_username("portfolio.html", zipped=zipped)

@app.route('/artifact/<path:dirpath>', methods=['GET'])
def artifact_dir(dirpath):
    username = session['username']
    filelist, dirlist = list_files_and_dirs(path_from_sessionuser_root(dirpath))
    return render_template_with_username("artifact.html", 
            ls=[(n, quote(n)) for n in filelist],
            dir=[(n, quote(n)) for n in dirlist],
            dirpath=quote(dirpath) + "/")

@app.route('/artifact/<path:dirpath>', methods=['POST'])
def artifact_dir_post(dirpath):
    makedir = unquote(request.form['directoryname'])
    file = request.files['file']
    if file:
        if allowed_file(file.filename) and check_filename(file.filename):
            file.save(path_from_sessionuser_root(dirpath, file.filename))
        else:
            sys.stderr.write("log> upload failed (unallowed name): %s\n" % repr(file.filename))
    elif makedir:
        os.mkdir(path_from_sessionuser_root(dirpath, makedir))

    filelist, dirlist = list_files_and_dirs(path_from_sessionuser_root(dirpath))
    return render_template_with_username("artifact.html", 
            ls=[(n, quote(n)) for n in filelist],
            dir=[(n, quote(n)) for n in dirlist],
            dirpath=quote(dirpath) + "/")

@app.route('/artifact', methods=['GET'])
def artifact_get():
    filelist, dirlist = list_files_and_dirs(path_from_sessionuser_root())
    return render_template_with_username("artifact.html",
            ls=[(n, quote(n)) for n in filelist],
            dir=[(n, quote(n)) for n in dirlist],
            dirpath="")

@app.route('/artifact', methods=['POST'])
def artifact_post():
    makedir = unquote(request.form['directoryname'])
    file = request.files['file']
    if file:
        if allowed_file(file.filename) and check_filename(file.filename):
            file.save(path_from_sessionuser_root(file.filename))
        else:
            sys.stderr.write("log> upload failed (unallowed name): %s\n" % repr(file.filename))
    elif makedir:
        os.mkdir(path_from_sessionuser_root(makedir))

    filelist, dirlist = list_files_and_dirs(path_from_sessionuser_root())
    return render_template_with_username("artifact.html",
            ls=[(n, quote(n)) for n in filelist],
            dir=[(n, quote(n)) for n in dirlist],
            dirpath="")

@app.route('/person', methods=['POST'])
def diary_post():
    return render_template_with_username("person.html");

@app.route('/person', methods=['GET'])
def diary():
    return render_template_with_username("person.html");

@app.route('/view_file/<path:filename>', methods=['GET'])
def view_file(filename):
    return send_from_directory(path_from_sessionuser_root(), filename)

# portfolioの新規作成ページ
@app.route('/new', methods=['GET'])
def new():
    filelist = os.listdir(path_from_sessionuser_root())
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
    filelist = os.listdir(path_from_sessionuser_root())
    filelist.sort()
    nonexist_i = None
    for i in range(1, 100):
        if ("portfolio%d.html" % i) not in filelist:
            nonexist_i = i
            break
    else:
        assert False, "too many portfolios"
    i = nonexist_i
    with open(os.path.join(path_from_sessionuser_root(), "portfolio%d.html" % i), "wb") as f:
        text = request.form["textarea"].encode('utf-8')
        f.write(text)
    return portfolio()

@app.route('/preview', methods=['POST'])
def preview():
    return request.form['textarea']

@app.route('/profile', methods=['GET'])
def profile():
    return render_template_with_username("profile.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template_with_username("page_not_found.html"), 404

if __name__ == '__main__':
    app.debug = True
    app.run() 
	
