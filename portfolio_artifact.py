import os
import sys
import urllib

from flask import session, request

from portfolio_common import render_template_with_username, path_from_sessionuser_root
from portfolio_common import ALLOWED_EXTENSIONS

def unquote(s):
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return urllib.unquote(s).decode('utf-8')

def quote(s):
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return urllib.quote(s)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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

def add_artifact_functions(app):
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


