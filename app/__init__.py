from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
# 表示数据库
migrate = Migrate(app, db)
# 添加数据库迁移引擎
# 注册flask插件的方式
from app import routes, models
