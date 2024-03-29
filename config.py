from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    SQLALCHEMY_DATABASE_URI = environ.get('MYSQLCREDS')
    SECRET_KEY = environ.get('SECKEY')
    EMAIL_INFO = environ.get('EMAIL_INFO')
