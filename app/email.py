#encoding:utf-8
#构造email
from email.mime.text import MIMEText
#from email.header import Header
#from email.utils import parseaddr,formataddr


#encoding:utf-8
from flask_mail import Message
from app import app,mail
from flask import render_template
from config import ADMINS

from email.header import Header
from email.utils import parseaddr, formataddr

from threading import Thread
from .decorators import async

def _formataddr(s):
    name,addr=parseaddr(s)
    return formataddr((Header(name,'utf-8').encode(),addr))

def mailMsg(subject, sender, recipients_name, recipients, text_body, html_body):
    msg=MIMEText(html_body,'html','utf-8')
    #构造发件人
    user=sender
    msg['From']=_formataddr('Microblog admin <%s>'%user)
    #构造收件人
    to_addr=recipients
    msg['To']=_formataddr('%s <%s>' % (recipients_name, to_addr))
    #构造邮件标题
    msg['Subject']=Header(subject,'utf-8')
    
    return msg


@async
def send_email(subject, sender, recipients_name, recipients, text_body, html_body):
    import smtplib
    #实例化一个smtp服务
    smtp=smtplib.SMTP()
    
    #连接网易邮件服务器提供的smtp服务
    smpt_host='smtp.163.com'
    smpt_port='25'
    smtp.connect(smpt_host,smpt_port)
    smtp.starttls()
    
    user='13672451429@163.com'
    password='zyx146'
    smtp.login(user, password)
    
    msg =  mailMsg(subject, sender, recipients_name, recipients, text_body, html_body)
    smtp.sendmail(user, [recipients], msg.as_string())
    
    smtp.quit()

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
    

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr))


def follower_notification(is_follow,followed, follower):
    '''
    关注，发送邮件提醒；取消关注，发送邮件提醒.
    #两个参数：被关注者，关注者（当前用户）
    '''
    subject = ""
    if is_follow:
        subject = "[microblog] %s is now following you!" % follower.nickname
    else: 
        subject = "[microblog] %s is now unfollowing you!" % follower.nickname
        
    send_email(subject,
               ADMINS[0],
               followed.nickname,
               followed.email,
               render_template('follower_email.txt',
                               user = followed, follower = follower, is_follow = is_follow),
               render_template('follower_email.html',
                               user = followed, follower = follower, is_follow = is_follow)
               )
               
