'''
定义表单类

'''

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length

from app.models import User


# 个人资料编辑器
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # 子类重新了构造函数，调用超类的方法，基础教程9.2.3使用函数super
        # super().__init__()也可以这样写
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')
'''
注册期间，我需要确保在表单中输入的用户名不存在于数据库中。 
在编辑个人资料表单中，我必须做同样的检查，但有一个例外。 
如果用户不改变原始用户名，那么验证应该允许，因为该用户名已经被分配给该用户。
'''


# 发布用户动态
class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')