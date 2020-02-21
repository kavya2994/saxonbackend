import jwt
import json
from datetime import datetime, timedelta
from flask import request
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields
from werkzeug.exceptions import NotFound, BadRequest, UnprocessableEntity, InternalServerError
from ...encryption import Encryption
from ...helpers import crossdomain
from ...models.users import Users
from ...models import status, roles
from ...api import api
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Ipaddress', type=str, location='json', required=True)
parser.add_argument('username', type=str, location='json', required=True)
parser.add_argument('password', type=str, location='json', required=True)

response_model = {
    'email': fields.String,
    'username': fields.String,
    'firstName': fields.String,
    'lastName': fields.String,
    'role': fields.String,
    'temppass': fields.Boolean(default=False),
    'token': fields.String,
    'securityQuestion': fields.String,
    'securityanswer': fields.Boolean,
    "timezone": fields.String,
    "language": fields.String
}


@ns.route('/login')
class Login(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Login',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        password = args['password']
        ip = args['Ipaddress']

        encrypt_password = Encryption().encrypt(password)
        userinfo = Users.query.filter_by(Username=username, Password=encrypt_password).first()
        if userinfo is None:
            LOG.debug("Auth failed. Username (%s) or Password is wrong", username)
            raise UnprocessableEntity('Username or Password is incorrect')

        if (userinfo.Status == status.STATUS_DELETE) or \
                (userinfo.Role in [roles.ROLES_REVIEW_MANAGER, roles.ROLES_ADMIN] and str(userinfo.Status).upper()
                 == status.STATUS_INACTIVE):
            LOG.debug("Auth failed. User is not active. Username:%s, status:%s, role:%s", username)
            raise UnprocessableEntity('User is not active')

        try:
            name = userinfo.DisplayName
            role = userinfo.Role
            exp = datetime.utcnow() + timedelta(hours=1, minutes=30)

            payload = {
                'username': username,
                'exp': exp,
                'role': role,
                'Ipaddress': ip,
            }

            token = jwt.encode(key=APP.config['JWT_SECRET'], algorithm='HS256', payload=payload, )
            token = token.decode('utf-8')
            securityQuestion = None if userinfo.SecurityQuestion is None else userinfo.SecurityQuestion.Question

            LOG.debug('User %s authenticated successfully', username)
            return {
                "email": userinfo.Email,
                "username": username,
                "firstName": name,
                "lastname": name,
                "role": role,
                "temppass": bool(userinfo.TemporaryPassword),
                'token': str(token),
                "securityQuestion": securityQuestion,
                "securityanswer": True if userinfo.SecurityAnswer is not None else False,
                "timezone": userinfo.Timezone,
                "language": userinfo.Language
            }

        except Exception as e:
            LOG.warning('Exception happened during authenticating user: %s', e)
            raise InternalServerError(e)
