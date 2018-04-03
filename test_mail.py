#coding: utf-8  
from email.mime.text import MIMEText
from email.header import Header

sender = '13672451429@163.com'
receiver = '13672451429@139.com'
subject = 'python email test'

msg = MIMEText( 'Hello Python', 'text', 'utf-8' )
to_addr='13672451429@139.com'
msg['To']=to_addr
msg['Subject'] = Header( subject, 'utf-8' )


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
smtp.sendmail(user, receiver, msg.as_string())
smtp.quit()
