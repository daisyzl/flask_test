# -*- coding:utf-8 -*-  
'''
function： 设置自定义错误页面
'''
from flask import render_template

from app import db

# 声明自定义的错误处理器
# @app.errorhandler(404)
from app.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


# @app.errorhandler(500)
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


'''
请注意这两个函数在模板之后返回第二个值，这是错误代码编号。 
对于之前我创建的所有视图函数，我不需要添加第二个返回值，因为我想要的是默认值200（成功响应的状态码）。 
本处，这些是错误页面，所以我希望响应的状态码能够反映出来。
'''