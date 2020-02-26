from flask_restplus import Resource
from . import ns
from ...helpers import RESPONSE_OK


@ns.route("/status")
class HealthStatus(Resource):
    def get(self):
        return RESPONSE_OK
