import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
# 添加类存储的变量
# app.config['POSTS_PER_PAGE'] 赋值方式
db = SQLAlchemy(app)
# 表示数据库
migrate = Migrate(app, db)
# 添加数据库迁移引擎
login = LoginManager(app)
login.login_view = 'login'
# 如果未登录的用户尝试查看受保护的页面，Flask-Login将自动将用户重定向到登录表单
# 'login'值是登录视图函数（endpoint）名，换句话说该名称可用于url_for()函数的参数并返回对应的URL

# 注册flask插件的方式
mail = Mail(app)
bootstrap = Bootstrap(app)


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                       backupCount=10)
    # RotatingFileHandler类非常棒，因为它可以切割和清理日志文件，以确保日志文件在应用运行很长时间时不会变得太大。
    # 本处，我将日志文件的大小限制为10KB，并只保留最后的十个日志文件作为备份。
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')
    # 日志文件的第一个有趣用途是，服务器每次启动时都会在日志中写入一行。
    # 当此应用在生产服务器上运行时，这些日志数据将告诉你服务器何时重新启动过。


from app import routes, models, errors
# flask中注册
