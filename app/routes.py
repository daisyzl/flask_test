from flask import render_template, flash, redirect, url_for

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'zhanglu'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', user=user, title='Home', posts=posts)


@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 如果是get请求则返回false，如果是post请求则返回true
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        # 使用这个技术来让用户知道某个动作是否成功
        # 当你调用flash()函数后，Flask会存储这个消息，但是却不会奇迹般地直接出现在页面上。
        # 模板需要将消息渲染到基础模板中，才能让所有派生出来的模板都能显示出来。
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
