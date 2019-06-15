'''
使用类来存储配置变量

'''

import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # 防止CSRF
