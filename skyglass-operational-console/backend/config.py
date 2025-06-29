import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
    FIRMS_API_KEY = os.environ.get('FIRMS_API_KEY')
    RAINVIEWER_API_KEY = os.environ.get('RAINVIEWER_API_KEY')
    OPENAQ_API_KEY = os.environ.get('OPENAQ_API_KEY')
