from flask import request
from flask_restplus import Resource
from .. import APP
from ..api import api
from ..helpers import crossdomain, RESPONSE_OK


@api.route("/my-ip", methods=["GET"])
@api.doc(description='Get user\'s IP address')
class MyIP(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def get(self):
        return {'ip': request.environ['REMOTE_ADDR']}



@api.route("/status", methods=["GET"])
@api.doc(description='Get Status of API Server')
class Status(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def get(self):
        return RESPONSE_OK
