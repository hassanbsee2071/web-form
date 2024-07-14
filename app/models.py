from app import db
from os import environ


class Deploy(db.Model):
    __tablename__ = environ.get("TABLE_NAME")
    id = db.Column(db.Integer, primary_key=True)
    tool = db.Column(db.String(1000), nullable=False)
    environment = db.Column(db.String(1000), nullable=False)
    hostname = db.Column(db.String(1000),  nullable=False)
    alias = db.Column(db.String(1000),  nullable=False)
    replicaset = db.Column(db.String(1000),  nullable=False)
    username = db.Column(db.String(1000),  nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    team = db.Column(db.String(1000), nullable=False)

    def __init__(
        self, id, tool, environment, hostname, alias, replicaset, username, password, team
    ):
        self.id = id
        self.tool = tool
        self.environment = environment
        self.hostname = hostname
        self.alias = alias
        self.replicaset = replicaset
        self.username = username
        self.password = password
        self.team = team
