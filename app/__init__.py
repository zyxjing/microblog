#encoding:utf-8

'''
让我们开始为我们的 app 包(文件 app/__init__.py )创建一个简单的初始化脚本:
上面的脚本简单地创建应用对象，接着导入视图模块，该模块我们暂未编写。
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import os
from flask_login import LoginManager
from flask_openid import OpenID
from config import basedir

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

oid = OpenID(app, os.path.join(basedir, 'tmp'))


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    
    app.logger.setLevel(logging.INFO)
    
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    
    app.logger.info('microblog startup')
    
    
from flask_msearch import Search
search = Search()
search.init_app(app)
search.create_index(update=True)

from flask_mail import Mail
mail = Mail(app)

from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)

from app import views,models

 