import os


class Config(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or "supersekrit"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
