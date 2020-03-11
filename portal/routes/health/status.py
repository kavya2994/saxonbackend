import os
from flask_restx import Resource
from flask import request
from . import ns
from ...helpers import RESPONSE_OK


@ns.route("/status")
class HealthStatus(Resource):
    def get(self):
        response = dict(RESPONSE_OK)
        response['version'] = os.getenv('GIT_VERSION', default='')
        response['actor'] = os.getenv('GIT_ACTOR', default='')
        response['date'] = os.getenv('DEPLOYMENT_TIME', default='')
        return response


@ns.route("/headers")
class HealthStatus(Resource):
    def get(self):
        response = dict(request.headers)
        return response
