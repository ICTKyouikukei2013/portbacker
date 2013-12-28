# -*- coding:utf-8 -*-

from portfolio_common import UPLOAD_FOLDER, IMAGE_EXTENSIONS
from portfolio_common import render_template_with_username, path_from_sessionuser_root

import os, datetime, itertools
from flask import Flask, session, request, redirect, send_from_directory, render_template
#gfrom werkzeug import secure_filename
import model

GRADE = [None, 'B1', 'B2', 'B3', 'B4', 'M1', 'M2', None, u'教員', u'職員']
GRADE_STR_TO_FORM_INDEX = {'B1': 1, 'B2': 2, 'B3': 3, 'B4': 4, 'M1': 5, 'M2': 6, u'教員': 8, u'職員': 9}
COURSE = [None, u'情報システムコース', u'情報デザインコース', u'複雑系知能コース', u'複雑系コース', u"高度ICTコース", u'未所属', None, u'教員', u'職員']
COURSE_STR_TO_FORM_INDEX = {u'情報システムコース': 1, u'情報デザインコース': 2, u'複雑系知能コース': 3, u'複雑系コース': 4, u"高度ICTコース": 5, u'未所属': 6, u'教員': 8, u'職員': 9}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def instance_of_ldap(username, password):
    return True

def get_date(filename):
    stat = os.stat(path_from_sessionuser_root(filename))
    last_modified = stat.st_mtime
    dt = datetime.datetime.fromtimestamp(last_modified)
    return dt.strftime("%Y/%m/%d")

def authentification(username, password):
    return True
    # return username == password

@app.before_request
def check_login_done():
    if 'static' in request.path.split('/'): # static files
        return
    if request.path == '/logout':
        return
    username = session.get('username')
    if username is not None:
        u = model.User.find(model.db, username)
        if u is None:
            return redirect('/logout')
        if request.path == '/login':
            return redirect('/')
        if request.path == '/profile' or request.path == '/logout':
            return
        if u.name == None or u.course == None or u.grade == None:
            return redirect('/profile')
        return
    if request.path == '/login':
        return
    return redirect('/login')

@app.route('/login', methods=['GET'])
def login_get():
    if session.get('username') is not None and authentification(session.get('username'), session.get('password')):
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
    u = model.User.find(model.db, username)
    if u is None:
        u = model.User(None, username, None, None, None)  # insert dummy user
        u.insert(model.db)
    session['displayname'] = u.name if u.name else None
    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    # remove the username from the session if its there
    session.pop('username', None)
    session.pop('displayname', None)
    return render_template("logout.html")

@app.route('/uploaded_file', methods=['GET'])
def uploaded_file():
    return 'success upload %s!' % request.args["filename"]

@app.route('/', methods=['GET'])
def index_page():
    return render_template_with_username("top.html")

@app.route('/goal_duplicated_error')
def goal_duplicated_error():
    return render_template("goal_duplicated_error.html")

@app.route('/goal', methods=['GET'])
def get_goal():
    username = session['username']
    goals = model.Goal.get(model.db, username)
    goal_texts = []
    graph_script = ""
    for goal in goals:
        goal_items = model.GoalItem.get(model.db, username, goal.serial)
        goal_texts.append([goal, goal_items])
        if not len(goal_items) == 0:
            #for goal_item in goal_items:
            #    sys.stderr.write("%s\n" % goal_item.change_data[-1])
            graph_script += create_graph(goal_items, goal.serial)
    return render_template_with_username("goal.html", goal_texts= goal_texts, graph_script = graph_script)

def create_graph(goal_items, canvas_id):
    count = 0
    total_graph_vertex = {}

    change_data_array = [goal_item.change_data[0]['datetime'] for goal_item in goal_items]
    change_data_array.sort()

    for change_data in change_data_array:
        create_date = (datetime.datetime.strptime(change_data.strftime("%Y-%m-%d"), "%Y-%m-%d"))
        count += 1
        total_graph_vertex.update({create_date: count})

    change_graph_vertex = {}
    for goal_item in goal_items:
        for change_data in goal_item.change_data:
            date = (datetime.datetime.strptime(change_data['datetime'].strftime("%Y-%m-%d"), "%Y-%m-%d"))
            if change_data['state']:
                try:
                    change_graph_vertex.update({date: change_graph_vertex[date]+1})
                except KeyError:
                    change_graph_vertex.update({date: 1})


    print total_graph_vertex
    print "aaaaaaaa"

    print change_graph_vertex
    print "aaaaaaaa"

    sdate = change_data_array[0]
    sx = 0
    sy = 120

    draw_script = """
    $( function () {
      var canvas = document.getElementById('%s');
      if ( ! canvas || ! canvas.getContext ) {
        return false;
      }
      var ctx = canvas.getContext('2d');
      ctx.beginPath();
      ctx.moveTo(%d, %d);""" % (canvas_id, sx, sy)

    for date, goal_item_count in sorted(total_graph_vertex.items()):
        diff_days = date.toordinal() - datetime.date(sdate.year, sdate.month, sdate.day).toordinal()
        print diff_days
        draw_script += """
      ctx.lineTo(%d, %d)""" % (sx + diff_days, sy - goal_item_count * 10)

    draw_script += """
      ctx.stroke();

      ctx.beginPath();
      ctx.strokeStyle = 'rgb(0, 255, 0)';
      ctx.moveTo(%d, %d);""" % (sx, sy)

    for date, done_count in sorted(change_graph_vertex.items(), reverse=True):
        diff_days = date.toordinal() - datetime.date(sdate.year, sdate.month, sdate.day).toordinal()
        print diff_days
        draw_script += """
      ctx.lineTo(%d, %d)""" % (sx + diff_days, sy - done_count * 10)

    draw_script += """
      ctx.stroke();
    });
    """

    return draw_script

@app.route('/goal_post_goal', methods=['POST'])
def post_goal():
    username = session['username']
    if request.form["button_name"] == "make":
        goal_title = request.form['goal_title']
        g = model.Goal(username, goal_title)
        try:
            g.insert(model.db)
        except model.GoalInsertedTwice:
            pass
        except model.GoalTitleDuplicated:
            return redirect('/goal_duplicated_error')
    return redirect('/goal')

@app.route('/remove_goal', methods=['POST'])
def remove_goal():
    username = session['username']
    if request.form["button_name"] == "remove":
        goal_serial = request.form["goal_serial"]
        assert goal_serial
        goal_serial = int(goal_serial)
        model.Goal.remove(model.db, username, goal_serial)
    return redirect('/goal')

@app.route('/goal_item', methods=['POST'])
def edit_goal_item():
    username = session['username']
    if request.form["edit_button"] == u"未完了" or request.form["edit_button"] == u"完了":
        goalitem_serial = request.form["goalitem_serial"]
        assert goalitem_serial
        goalitem_serial = int(goalitem_serial)
        itemc = model.GoalItem.find(model.db, username, goalitem_serial)
        itemc.change_data.append({"datetime": datetime.datetime.today(), "state": not itemc.change_data[-1]["state"]})
        itemc.update(model.db)
    elif request.form["edit_button"] == u"削除":
        goalitem_serial = request.form["goalitem_serial"]
        assert goalitem_serial
        goalitem_serial = int(goalitem_serial)
        model.GoalItem.remove(model.db, username, goalitem_serial)
    return redirect('/goal')

@app.route('/goal_post_goal_item', methods=['POST'])
def post_goal_item():
    username = session['username']
    if request.form["button_name"] == "make":
        goal_item_title = request.form["goal_item_title"]
        goal_serial = request.form['goal_serial']
        try:
            goal_serial = int(goal_serial)
        except:
            return redirect('/goal')
        change_data = [{"datetime": datetime.datetime.today(), "state": False}]
        gi = model.GoalItem(username, goal_serial, goal_item_title, change_data, True)
        try:
            gi.insert(model.db)
        except model.GoalItemInsertedTwice:
            pass
        except model.GoalItemTitleDuplicated:
            return redirect('/goalitem_duplicated_error')
    return redirect('/goal')

@app.route('/personallog', methods=['GET'])
def personallog_get():
    username = session['username']
    goals = model.Goal.get(model.db, username)
    goal_texts = []
    for goal in goals:
        goal_items = model.GoalItem.get(model.db, username, goal.serial)
        goal_texts.append([goal, goal_items])
    logitem_texts = []
    for item in model.ItemLog.get(model.db, username):
        logitem_texts.append((item.get_goalitem_title(model.db), item))
    return render_template_with_username("/personallog.html", goal_texts= goal_texts, logitem_texts=logitem_texts)

@app.route('/personallog', methods=['POST'])
def personallog_post():
    username = session['username']
    if request.form["button"] == u"入力":
        personallog_text = request.form['personallog_text']
        try:
            goalitem_serial = int(request.form["goal_item_serial"])
        except:
            return redirect('/personallog')
        if personallog_text:
            item_log = model.ItemLog(username, goalitem_serial, datetime.datetime.today(), personallog_text)
            item_log.insert(model.db)
    elif request.form["button"] == u"削除":
        sys.exit("NOT-YET implemented!!!!")
        rmlog = request.form['rmgoal']
        sys.stderr.write("goalitem_serial=%s\n" % request.form["goal_item_serial"])
    return redirect('/personallog')

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
    textarea = request.form['textarea']
    return render_template_with_username("preview.html", textarea=textarea)

def render_profile_page_with_user_obj(uid, uobj):
    course_index = COURSE_STR_TO_FORM_INDEX.get(uobj.course, 0)
    grade_index = GRADE_STR_TO_FORM_INDEX.get(uobj.grade)
    name = uobj.name
    return render_template_with_username("profile.html", 
            uid=uid, name=name, course_index=course_index, grade_index=grade_index,
            show_tabs=1)

@app.route('/profile', methods=['GET'])
def profile():
    uid = session.get("username")
    uobj = model.User.find(model.db, uid)
    if uobj and not (not uobj.name or not uobj.course or not uobj.grade):  # if user exists and not a dummy user
        return render_profile_page_with_user_obj(uid, uobj)
    else:
        return render_template_with_username("profile.html", 
                uid=uid, name='', course_index=0, grade_index=0,
                show_tabs=0)

import sys

@app.route('/profile', methods=['POST'])
def setting_profile():
    uid = session.get("username")
    name = request.form['name']
    grade = request.form['grade']
    course = request.form['course']
    show_tabs = request.form['show_tabs']
    try:
        course = int(course)
        grade = int(grade)
        show_tabs = int(show_tabs)
    except:
        course = grade = show_tabs = 0
    if not name or not grade or not course:
        return render_template_with_username("profile.html", 
                uid=uid, name=name, course_index=course, grade_index=grade,
                show_tabs=show_tabs)
    sys.stderr.write("course = %s, grade = %s\n" % (repr(course), repr(grade)))
    uobj = model.User(name, session.get('username'), None, COURSE[int(course)], GRADE[int(grade)])
    uobj.update(model.db)
    session['displayname'] = uobj.name if uobj.name else None
    return redirect("/")

@app.errorhandler(404)
def page_not_found(error):
    return render_template_with_username("page_not_found.html"), 404

if __name__ == '__main__':
    from portfolio_artifact import add_artifact_functions

    # set the secret key.  keep this really secret:
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

    add_artifact_functions(app)

    app.debug = True
    # app.run(host='49.212.234.134')
    app.run() 

