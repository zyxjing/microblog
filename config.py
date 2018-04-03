CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' },
    { 'name': 'openid', 'url' : 'http://<username>.openid.org.cn' }
]

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


#pagination
POSTS_PER_PAGE = 3

MSEARCH_INDEX_NAME = 'whoosh_index'
MSEARCH_BACKEND = 'whoosh'
MSEARCH_ENABLE = True
#配置配置 Flask-WhooshAlchemy 也是相当简单。我们只需要告诉扩展全文搜索数据库的名称(文件 config.py):
WHOOSH_BASE = os.path.join(basedir, 'whoosh_base')
#搜索结果最大显示50条
MAX_SEARCH_RESULTS = 50

# mail server settings
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 465
MAIL_USE_TLS = True
MAIL_USE_SSL = True
#MAIL_DEBUG = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['13672451429@163.com']