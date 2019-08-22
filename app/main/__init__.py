# -*- coding:utf-8 -*-  
'''
function：
'''
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes