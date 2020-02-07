import jwt
import json
from datetime import datetime, timedelta
from flask import request
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from ...encryption import Encryption
from ...models.users import Users
from ...api import api
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Username', type=str, location='json', required=True)
parser.add_argument('Password', type=str, location='json', required=True)

@ns.route('/login')
class Login(Resource):
    @ns.doc(parser=parser,
        description='Login',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        try:
            username = args['Username']
            password = args['Password']
            encrypt_password = Encryption().encrypt(password)
            userinfo = Users.query.filter_by(Username=username, Password=encrypt_password, Status="active").first()

            if userinfo == None:
                print("Username or password is incorrect")
                return "Username or password is incorrect", 401

            name = userinfo.DisplayName
            role = userinfo.Role
            exp = datetime.utcnow() + timedelta(hours=1, minutes=30)
            payload = {'User': username, 'Exp': str(exp), 'Role': role, 'IP': args['IP'] if 'IP' in args else '' }
            token = jwt.encode(key='secret', algorithm='HS256', payload=payload,)
            token = token.decode('utf-8')

            return {
                    "fusername": "test@test.com",
                    "fpass": "test001",
                    "id": username,
                    "username": username,
                    "firstName": name, "lastname": name, "role": role,
                    "TemporaryPassword": userinfo.TemporaryPassword,
                    'token': str(token),
                    "SecurityQuestion": userinfo.SecurityQuestionID,
                    "Email": userinfo.Email,
                    }, 200

        except json.decoder.JSONDecodeError:
            return 'Bad Request', 400

        except Exception as e:
            print(str(e))
            print("in exception", e)
            return "cant connect: " + str(e), 500

