import jwt
import json
from flask import request
from flask_restplus import Resource, reqparse, cors
from werkzeug.exceptions import Unauthorized
from . import ns
from ... import APP
from ...helpers import token_verify_or_raise, crossdomain

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route('/token/check')
class TokenCheck(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Validates the user token',
            responses={400: 'Bad Request', 401: 'Unauthorized', 200: 'OK'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth["username"] != args["username"] or auth["Ipaddress"] != args["Ipaddress"]:
            raise Unauthorized()

        return {"result": True}
