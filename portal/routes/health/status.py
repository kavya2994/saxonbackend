from flask_restplus import Resource
from ...api import api
from ...helpers import RESPONSE_OK


# Please do not delete this.
# This is being used to make identify if the app is up and running or not
ns = api.namespace('health')

@ns.route("/status")
class HealthStatus(Resource):
    def get(self):
        return RESPONSE_OK
