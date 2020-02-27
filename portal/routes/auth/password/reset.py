import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort
from flask_restx import Resource, reqparse, cors, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ....helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise, RESPONSE_OK
from ....encryption import Encryption
from ....models import db
from ....models.users import Users
from ....models.security_question import SecurityQuestion
from ....services.mail import send_email
from .. import ns
from .... import APP, LOG


parser = reqparse.RequestParser()
parser.add_argument('request_type', type=str, location='json', required=True,
                    help='Accepted Values: [Admin|SecurityQuestion|Email]')
parser.add_argument('username', type=str, location='json', required=True)
parser.add_argument('Answer', type=str, location='json', required=False)
parser.add_argument('Email', type=str, location='json', required=False)

response_model = ns.model('PostPasswordReset', {
    'result': fields.String,
})

def _change_password(username, email, display_name):
    try:
        password = randomStringwithDigitsAndSymbols()
        pass_encrypt = Encryption().encrypt(password)
        message = f'<p>Dear {display_name}</p>' + \
                f'<p>Your password has been reset.</p>' + \
                f'<p>The temporary password is: {password}</p>'

        user = Users.query.filter_by(Username=username).first()
        user.Password = pass_encrypt
        user.TemporaryPassword = True
        db.session.commit()

        send_email(to_address=email, subject='Reset Password', body=message)
        return RESPONSE_OK

    except Exception as e:
        LOG.warning('Unexpected error happened during changing password: %s', e)
        raise InternalServerError()


@ns.route("/password/reset")
class PasswordReset(Resource):
    @ns.doc(parser=parser,
            description='Reset Password',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 422: 'UnprocessableEntity',
                       500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        change_pass = False

        username = args["username"]
        # token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        user = Users.query.filter_by(Username=username).first()
        if user is None:
            raise UnprocessableEntity('User not found')

        if args['request_type'] == 'SecurityQuestion':
            if 'Answer' not in args or user.SecurityAnswer != Encryption().encrypt(args['Answer']):
                raise UnprocessableEntity('Invalid Answer')

        elif args['request_type'] == 'Email':
            if 'Email' not in args or user.Email != args['Email']:
                raise UnprocessableEntity('User not found/ Email is not valid')

        elif args['request_type'] == 'Admin':
            pass

        else:
            raise BadRequest('Invalid RequestType')

        return _change_password(username, user.Email, user.DisplayName)
