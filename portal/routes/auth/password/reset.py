import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort
from flask_restplus import Resource, reqparse, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ....helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise, crossdomain, RESPONSE_OK
from ....encryption import Encryption
from ....models import db
from ....models.users import Users
from ....models.security_question import SecurityQuestion
from ....services.mail import send_email
from .. import ns
from .... import APP


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('ipAddress', type=str, location='headers', required=True)

parser.add_argument('RequestType', type=str, location='json', required=True, help='Accepted Values: [Admin|SecurityQuestion|Email]')
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Answer', type=str, location='json', required=False)
parser.add_argument('Email', type=str, location='json', required=False)

@ns.route("/password/reset")
class PasswordReset(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
        description='Reset Password',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 422: 'UnprocessableEntity', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        change_pass = False

        username = args["username"]
        token = token_verify_or_raise(token=args["Authorization"], ip=args["ipAddress"], user=args["username"])

        user = Users.query.filter_by(Username=username).first()
        if user == None:
            raise UnprocessableEntity('User not found')

        if args['RequestType'] == 'SecurityQuestion':
            if 'Answer' not in args or user['Answer'] != Encryption().encrypt(args['Answer']):
                raise UnprocessableEntity('Invalid Answer')

        elif args['RequestType'] == 'Email':
            if 'Email' not in args or user["Email"] != args['Email']:
                raise UnprocessableEntity('User not found')

        elif args['RequestType'] == 'Admin':
            pass

        else:
            raise BadRequest('Invalid RequestType')

        return self._change_pass(username, user.Email)

    def _change_password(self, username, email):
        try:
            password = randomStringwithDigitsAndSymbols()
            pass_encrypt = Encryption().encrypt(password)
            message = f'<p>Your password has been reset. The temporary password is: {password}</p>' + \
                    '<p>Please log into your system as soon as possible to set your new password.</p>'

            user = Users.query.filter_by(Username=username).first()
            user.Password = pass_encrypt
            user.TemporaryPassword = True
            db.session.commit()

            send_email(to_address=email, subject='Reset Password', body=message)
            return RESPONSE_OK

        except Exception as e:
            print(str(e))
            raise InternalServerError()
