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
@ns.route('/login')
class Login(Resource):
    @ns.doc(parser=parser,
        description='Login',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        print(request.headers)
        print(request.get_data())
        print(request.data)
        print(request.remote_addr)
        print("####################")

        try:
            data = json.loads(str(request.data, encoding='utf-8'))

            if 'Username' not in data:
                return "'Username' is required", 400

            if 'Password' not in data:
                return "'Password' is required", 400

            print(data)
            username = data['Username']
            password = data["Password"]
            userinfo = Users.query.filter_by(Username=username).first()
            encrypt_password = Encryption().encrypt(password)
            print(userinfo)
            # print(list(userinfo.keys()))
            # print(userinfo["password"])

            if userinfo != None and userinfo["Password"] == encrypt_password and str(userinfo["Status"]).lower() == "active":
                if "TemporaryPassword" in userinfo.keys():
                    # print(request.form)
                    name = userinfo["DisplayName"]
                    role = userinfo["Role"]
                    exp = datetime.utcnow()
                    if userinfo["Role"] == "reviewermanager":
                        exp += timedelta(hours=1, minutes=30)
                    else:
                        # exp += timedelta(minutes=30)
                        exp += timedelta(hours=1, minutes=30)

                    encode = jwt.encode({'User': username, 'exp': exp, 'IP': data["ip"], "role": role},
                                        'secret', algorithm="HS256")

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
            return "cant connect" + str(e), 500

