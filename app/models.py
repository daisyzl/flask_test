# -*- coding:utf-8 -*-  
'''
function：
'''
from _md5 import md5
from datetime import datetime
from time import time

import jwt
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, app

# 除了外键没有其他数据的辅助表
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


# Flask-Login插件需要在用户模型上实现某些属性和方法，UserMixin添加到模型中
'''
is_authenticated: 一个用来表示用户是否通过登录认证的属性，用True和False表示。
is_active: 如果用户账户是活跃的，那么这个属性是True，否则就是False
（译者注：活跃用户的定义是该用户的登录状态是否通过用户名密码登录，通过“记住我”功能保持登录状态的用户是非活跃的）。
is_anonymous: 常规用户的该属性是False，对特定的匿名用户是True。
get_id(): 返回用户的唯一id的方法，返回值类型是字符串(Python 2下返回unicode字符串).
'''
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # backref参数定义了代表“多”的类的实例反向调用“一”的时候的属性名称。这将会为用户动态添加一个属性post.author，
    # 调用它将返回给该用户动态的用户实例。
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # chapter8 粉丝
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # 查询来检查两个用户之间的关系是否已经存在
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    # 生成令牌
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


# 用户会话是Flask分配给每个连接到应用的用户的存储空间，Flask-Login通过在用户会话中存储其唯一标识符来跟踪登录用户。
# 每当已登录的用户导航到新页面时，Flask-Login将从会话中检索用户的ID，然后将该用户实例加载到内存中。
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
# 用户登录
# 这里的功能使用不明白，chapter5 用户加载函数

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 自动设置类名为小写来作为对应表的名称

    def __repr__(self):
        return '<Post {}>'.format(self.body)

