import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse
from werkzeug.exceptions import InternalServerError

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.jwttokenblacklist import JWTTokenBlacklist
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/logout")
class Logout(Resource):
    @ns.doc(description='Create New User',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])
        blacklist = JWTTokenBlacklist(JWTToken=args["Authorization"],
                                      LoggedOutTime=datetime.utcnow())
        try:
            db.session.add(blacklist)
            db.session.commit()
        except Exception as e:
            LOG.error(e)
            raise InternalServerError()
