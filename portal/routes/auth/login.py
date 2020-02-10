import jwt
import json
from datetime import datetime, timedelta
from flask import request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields
from werkzeug.exceptions import NotFound, BadRequest, UnprocessableEntity, InternalServerError
from ...encryption import Encryption
from ...models.users import Users
from ...api import api
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('IpAddress', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='json', required=True)
parser.add_argument('Password', type=str, location='json', required=True)

response_model = {
    'Email': fields.String,
    'Username': fields.String,
    'FirstName': fields.String,
    'LastName': fields.String,
    'Role': fields.String,
    'TemporaryPassword': fields.Boolean(default=False),
    'Token': fields.String,
    'SecurityQuestion': fields.String,
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
        username = args['Username']
        password = args['Password']
        ip = args['IpAddress']

        encrypt_password = Encryption().encrypt(password)
        userinfo = Users.query.filter_by(Username=username, Password=encrypt_password).first()

        if userinfo == None:
            print("Username or password is incorrect")
            raise UnprocessableEntity('Username or Password is incorrect')

        if userinfo.Status != "active":
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

            token = jwt.encode(key=app.config['JWT_SECRET'], algorithm='HS256', payload=payload,)
            token = token.decode('utf-8')

            return {
                    "Email": userinfo.Email,
                    "Username": username,
                    "FirstName": name,
                    "lastname": name,
                    "Role": role,
                    "TemporaryPassword": userinfo.TemporaryPassword,
                    'Token': str(token),
                    "SecurityQuestion": userinfo.SecurityQuestion.Question,
            }

        except json.decoder.JSONDecodeError:
            raise BadRequest

        except Exception as e:
            print(str(e))
            print("in exception", e)
            raise InternalServerError(e)

