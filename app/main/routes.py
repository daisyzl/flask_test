from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm
from app.main.forms import PostForm
from app.models import User, Post
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# POST请求，视图函数处理接收的表单数据
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
# 该函数将受到保护，不允许未经身份验证的用户访问
# @login_required添加到位于@app.route装饰器下面的视图函数上
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        # 利用外键
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    # 通过重定向来响应Web表单提交产生的POST请求是一种标准做法。chapter9 分页
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    # Flask-SQLAlchemy的所有查询对象都支持paginate()方法，原生就支持分页
    # 从1开始的页码
    # 每页的数据量
    # 错误处理布尔标记，如果是True，当请求范围超出已知范围时自动引发404错误。如果是False，则会返回一个空列表。
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',  title='Home Page', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # 当有结果时它的工作方式与first()完全相同，但是在没有结果的情况下会自动发送404 error给客户端。
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
'''
当validate_on_submit()返回False时，可能是由于两个不同的原因。
这可能是因为浏览器刚刚发送了一个GET请求，我需要通过提供表单模板的初始版本来响应。
也可能是这种情况，浏览器发送带有表单数据的POST请求，但该数据中的某些内容无效。
对于该表单，我需要区别对待这两种情况。
当第一次请求表单时，我用存储在数据库中的数据预填充字段，所以我需要做与提交相反的事情，
那就是将存储在用户字段中的数据移动到表单中，这将确保这些表单字段具有用户的当前数据。
但在验证错误的情况下，我不想写任何表单字段，因为它们已经由WTForms填充了。
为了区分这两种情况，我需要检查request.method，如果它是GET，这是初始请求的情况，如果是POST则是提交表单验证失败的情况。

'''


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    # 分页
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    # url_for()函数的一个有趣的地方是，你可以添加任何关键字参数，
    # 如果这些参数的名字没有直接在URL中匹配使用，
    # 那么Flask将它们设置为URL的查询字符串参数。
    return render_template('index.html', title='Explore',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)