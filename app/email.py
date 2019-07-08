# -*- coding:utf-8 -*-  
'''
function：
'''
from threading import Thread

from flask import render_template
from flask_mail import Message

from app import mail, app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
# 应用上下文
# https://www.cnblogs.com/guoxiaoyan/p/9465374.html


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
    # 电子邮件的发送将在线程中运行，并且当进程完成时，线程将结束并自行清理。
    # 当应用启动自定义线程时，可能需要手动创建这些线程的上下文。


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))