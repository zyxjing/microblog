#encoding:utf-8
from flask_mail import Message
from app import app,mail
from flask import render_template
from config import ADMINS

from email.header import Header
from email.utils import parseaddr, formataddr

from threading import Thread
from .decorators import async


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr))


def follower_notification(followed, follower):
    '''
    #两个参数：被关注者，关注者（当前用户）
    '''
    From = _format_addr(u'Microblog admin <%s>' % ADMINS[0])
    send_email("[microblog] %s is now following you!" % follower.nickname,
               From,
               #[followed.email],
               ['13672451429@126.com'],
               render_template('follower_email.txt',
                               user = followed, follower = follower),
               render_template('follower_email.html',
                               user = followed, follower = follower)
               )
               
    