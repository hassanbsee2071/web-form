import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from os import environ


# create the application instance
app = Flask(__name__)
app.config.from_object(Config)

# setting logger
logging.basicConfig(level=logging.DEBUG if Config.DEBUG == "TRUE" else logging.INFO)
logger = logging.getLogger("Almosafer Database Tool")

# create the application database instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models