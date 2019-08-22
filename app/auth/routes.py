from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm,  ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # 假设用户已经登录，却导航到应用的*/login* URL
    form = LoginForm()
    if form.validate_on_submit():
        # 如果是get请求则返回false，如果是post请求则返回true
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # 将用户登录状态注册为已登录
        # 用户导航到任何未来的页面时，应用都会将用户实例赋值给current_user变量
        next_page = request.args.get('next')
        # 重定向后相对url
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        '''
        实际上有三种可能的情况需要考虑，以确定成功登录后重定向的位置：
        如果登录URL中不含next参数，那么将会重定向到本应用的主页。
        如果登录URL中包含next参数，其值是一个相对路径（换句话说，该URL不含域名信息），那么将会重定向到本应用的这个相对路径。
        如果登录URL中包含next参数，其值是一个包含域名的完整URL，那么重定向到本应用的主页。
        前两种情况很好理解，第三种情况是为了使应用更安全。 
        攻击者可以在next参数中插入一个指向恶意站点的URL，因此应用仅在重定向URL是相对路径时才执行重定向，这可确保重定向与应用保持在同一站点中。 
        为了确定URL是相对的还是绝对的，我使用Werkzeug的url_parse()函数解析，然后检查netloc属性是否被设置。
        '''
        return redirect(next_page)
        # 要求用户登录 知识点  chapter5

        # flash('Login requested for user {}, remember_me={}'.format(
        #     form.username.data, form.remember_me.data))
        # 使用这个技术来让用户知道某个动作是否成功
        # 当你调用flash()函数后，Flask会存储这个消息，但是却不会奇迹般地直接出现在页面上。
        # 模板需要将消息渲染到基础模板中，才能让所有派生出来的模板都能显示出来。
        # return redirect(url_for('index'))
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    # 对应于login_user
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
