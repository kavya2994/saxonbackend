from flask import request
from flask_restplus import Resource
from ..api import api


@api.route("/my-ip", methods=["GET"])
@api.doc(description='Get user\'s IP address')
class MyIP(Resource):
    def get(self):
        print(request.headers)
        return {'ip': request.environ['REMOTE_ADDR']}, 200
