# -*- coding:utf-8 -*-

import sys, os
sys.path.append('/home/project20/portbacker')

import portfolio_common
portfolio_common.UPLOAD_FOLDER = u"/var/www/portbacker/data/"

from portfolio import app as application
