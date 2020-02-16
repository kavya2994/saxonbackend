import jwt
import json
from datetime import datetime, timedelta
from flask import request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields
from werkzeug.exceptions import NotFound, BadRequest, UnprocessableEntity, InternalServerError
from ...encryption import Encryption
from ...models.users import Users
from ...models import status
from ...api import api
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('ip', type=str, location='json', required=True)
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
}


@ns.route('/login')
class Login(Resource):
    @ns.doc(parser=parser,
            description='Login',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        password = args['password']
        ip = args['ip']

        encrypt_password = Encryption().encrypt(password)
        userinfo = Users.query.filter_by(Username=username, Password=encrypt_password).first()
        print(userinfo.Username)
        if userinfo == None:
            print("Username or password is incorrect")
            raise UnprocessableEntity('Username or Password is incorrect')

        if userinfo.Status == status.STATUS_DELETE:
            raise UnprocessableEntity('User is not active')

        try:
            name = userinfo.DisplayName
            role = userinfo.Role
            exp = datetime.utcnow() + timedelta(hours=1, minutes=30)

            payload = {
                'Username': username,
                'Exp': str(exp),
                'Role': role,
                'IpAddress': ip,
            }

            token = jwt.encode(key=app.config['JWT_SECRET'], algorithm='HS256', payload=payload, )
            token = token.decode('utf-8')
            securityQuestion = None if userinfo.SecurityQuestion is None else userinfo.SecurityQuestion.Question

            return {
                "email": userinfo.Email,
                "username": username,
                "firstName": name,
                "lastname": name,
                "role": role,
                "temppass": userinfo.TemporaryPassword,
                'token': str(token),
                "securityQuestion": securityQuestion,
            }

        except json.decoder.JSONDecodeError:
            raise BadRequest

        except Exception as e:
            print(str(e))
            print("in exception", e)
            raise InternalServerError(e)
