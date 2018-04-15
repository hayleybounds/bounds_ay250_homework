
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Super Secret PASSWORD'
    DEBUG = True
    
    
class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = \
        'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Super Secret PASSWORD'
    TESTING = True
    DEBUG = True