import os

from flask import session, render_template

UPLOAD_FOLDER = u'./data'
DOCUMENT_EXTENSIONS = frozenset(['txt', 'pdf', 'md'])
IMAGE_EXTENSIONS = frozenset(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS = DOCUMENT_EXTENSIONS.union(IMAGE_EXTENSIONS)

def render_template_with_username(url,**keywordargs):
    username = session.get('displayname')
    if not username:
        username = session.get('username')
    return render_template(url,username=username,**keywordargs)

def path_from_sessionuser_root(*p):
    s = [UPLOAD_FOLDER, session['username']]
    s.extend(p)
    return os.path.join(*s)

