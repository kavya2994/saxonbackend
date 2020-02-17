import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.users import Users
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


response_model = {
    "Username": fields.String,
    "DisplayName": fields.String,
    "Email": fields.String,
    "Language": fields.String,
    "Timezone": fields.String
}


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/profile/get")
class GetProfileDetails(Resource):
    @ns.doc(parser=parser,
            description='Get profile details',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['IpAddress']

        decoded_token = token_verify_or_raise(token, username, ip)
        users = Users.query.filter_by(Username=username).first()
        return {
                   "Username": users.Username,
                   "DisplayName": users.DisplayName,
                   "Email": users.Email,
                   "Language": users.Language,
                   "Timezone": users.Timezone
               }, 200
