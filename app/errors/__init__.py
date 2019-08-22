# -*- coding:utf-8 -*-  
'''
function：
'''
from flask import Blueprint

bp = Blueprint('errors', __name__)
# Blueprint对象创建后，我导入了handlers.py模块，
# 以便其中的错误处理程序在blueprint中注册。
from app.errors import handlers