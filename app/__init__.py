from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
# 表示数据库
migrate = Migrate(app, db)
# 添加数据库迁移引擎
login = LoginManager(app)
login.login_view = 'login'
# 如果未登录的用户尝试查看受保护的页面，Flask-Login将自动将用户重定向到登录表单
# 注册flask插件的方式
from app import routes, models
