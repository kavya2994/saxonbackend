import jwt
import json
from flask import request, current_app as app
from flask_restplus import Resource, reqparse
from werkzeug.exceptions import Unauthorized
from . import ns
from ...helpers import token_verify_or_raise


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

@ns.route('/token/check')
class TokenCheck(Resource):
    @ns.doc(parser=parser,
        description='Validates the user token',
        responses={400: 'Bad Request', 401: 'Unauthorized', 200: 'OK'})

    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["IpAddress"], user=args["Username"])

        if auth["Username"] != args["Username"] or auth["IpAddress"] != args["IpAddress"]:
            raise Unauthorized()

        return { "result": True }
