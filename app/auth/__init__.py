# -*- coding:utf-8 -*-  
'''
function：
'''
from flask import Blueprint
bp = Blueprint('auth', __name__)

from app.auth import routes