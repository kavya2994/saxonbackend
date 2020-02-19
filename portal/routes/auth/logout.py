import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, crossdomain, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.jwttokenblacklist import JWTTokenBlacklist
from ...services.mail import send_email
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/logout")
class Logout(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Create New User',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)