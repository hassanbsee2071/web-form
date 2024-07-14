""" schema classes """
from app import app
from flask_marshmallow import Marshmallow
from app.models import Deploy

ma = Marshmallow(app)


class DeploySchema(ma.ModelSchema):
    class Meta:
        model = Deploy
        fields = (
            "id",
            "tool",
            "environment",
            "hostname",
            "alias",
            "replicaset",
            "username",
            "password",
            "team",
        )  

deployments_schema = DeploySchema(many=True)