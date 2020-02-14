import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ....helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise, crossdomain
from ....encryption import Encryption
from ....models import db
from ....models.users import Users
from ....models.security_question import SecurityQuestion
from .. import ns
from .... import APP


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

parser.add_argument('Username', type=str, location='json', required=True)
parser.add_argument('OldPassword', type=str, location='json', required=True)
parser.add_argument('NewPassword', type=str, location='json', required=True)

@ns.route("/password/change")
class PasswordChange(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @ns.doc(parser=parser,
        description='Change Password',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 422: 'UnprocessableEntity', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def post(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["IpAddress"], user=args["Username"])

        # TODO:
        # Verify the role from token before proceeding with password chanaging

        username = args["Username"]
        old_pass = args["OldPassword"]
        new_pass = args["NewPassword"]

        user = Users.query.filter_by(Username=username).first()
        if user is None:
            raise UnprocessableEntity('Username is not valid')

        if user.Password != Encryption().encrypt(old_pass):
            raise BadRequest('Old Password is wrong')

        try:
            user.Password = Encryption().encrypt(new_pass)
            user.TemporaryPassword = False
            db.session.commit()
            return {"result": "Password changed successfully"}

        except KeyError as e:
            print(e)
            raise InternalServerError()

