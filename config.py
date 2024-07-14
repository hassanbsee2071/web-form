from os import environ


# config class
class Config(object):
    """set Flask configuration variables from .env file."""
    DEBUG = environ.get("DEBUG")
    # sqlalchemy
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    SQLALCHEMY_POOL_TIMEOUT = int(environ.get("SQLALCHEMY_POOL_TIMEOUT"))
    SQLALCHEMY_POOL_RECYCLE = int(environ.get("SQLALCHEMY_POOL_RECYCLE"))

 