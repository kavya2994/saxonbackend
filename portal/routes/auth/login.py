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
parser.add_argument('IP', type=str, location='json', required=False)

@ns.route('/login')
class Login(Resource):
    @ns.doc(parser=parser,
        description='Login',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        try:
            username = args['Username']
            password = args["Password"]
            userinfo = Users.query.filter_by(Username=username).first()
            encrypt_password = Encryption().encrypt(password)

            if userinfo != None and userinfo["Password"] == encrypt_password and str(userinfo["Status"]).lower() == "active":
                if "TemporaryPassword" in userinfo.keys():
                    name = userinfo["DisplayName"]
                    role = userinfo["Role"]
                    exp = datetime.utcnow() + timedelta(hours=1, minutes=30)

                    encode = jwt.encode(key='secret', algorithm='HS256',
                        payload={'User': username, 'Exp': exp, 'IP': data["IP"], "Role": role },)

                    return {"fusername": "test@test.com", "fpass": "test001", "id": username, "username": username,
                                    "firstName": name, "lastname": name, "role": role,
                                    "TemporaryPassword": userinfo["TemporaryPassword"],
                                    'token': str(encode.decode('utf-8')),
                                    "SecurityQuestion": ("SecurityQuestionID" in userinfo.keys()),
                                    "Email": userinfo["Email"]}, 200
                else:
                    return "Cant find temppass field", 401

            else:
                print("Username or password is incorrect")
                return "Username or password is incorrect", 401
        except json.decoder.JSONDecodeError:
            return 'Bad Request', 400

        except Exception as e:
            print(str(e))
            print("in exception")
            return "cant connect: " + str(e), 500

