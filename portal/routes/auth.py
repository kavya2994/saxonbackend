import jwt
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from ..encryption import Encryption
from ..models.users import Users


auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates')

@auth_blueprint.route('/checktoken', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
def checktoken():
    if request.method == "POST":
        result = False
        print(request.headers)
        try:
            token = ""
            request_keys = request.headers.keys()
            if "Authorization" in request_keys and "Ipaddress" in request_keys and "User" in request_keys:
                token = request.headers["Authorization"]
                print(token)
            print(request.get_data())
            data = json.loads(str(request.data, encoding='utf-8'))
            decoded = jwt.decode(token, key='secret')
            print(decoded["user"])
            if decoded["user"] == request.headers["User"] and decoded["ip"] == request.headers["Ipaddress"]:
                result = True
        except jwt.DecodeError:
            print("decode error")
            result = False
        except jwt.ExpiredSignatureError:
            print("sign")
            result = False
        except KeyError:
            print("key error")
            print(result)
        if result:
            return jsonify({"result": result}), 200
        else:
            return jsonify({"result": result}), 401


@auth_blueprint.route('/login1', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['*'], allow_headers=['Content-Type'])
def login():
    if request.method == "POST" or request.method == "OPTIONS":
        print(request.headers)
        print(request.get_data())
        print(request.data)
        print(request.remote_addr)
        print("####################")

        try:
            data = json.loads(str(request.data, encoding='utf-8'))

            if 'Username' not in data:
                return jsonify("'Username' is required"), 400

            if 'Password' not in data:
                return jsonify("'Password' is required"), 400

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

                    encode = jwt.encode({'user': username, 'exp': exp, 'ip': data["ip"], "role": role},
                                        'secret', algorithm="HS256")

                    return jsonify({"fusername": "test@test.com", "fpass": "test001", "id": username, "username": username,
                                    "firstName": name, "lastname": name, "role": role,
                                    "TemporaryPassword": userinfo["TemporaryPassword"],
                                    'token': str(encode.decode('utf-8')),
                                    "SecurityQuestion": ("SecurityQuestionID" in userinfo.keys()),
                                    "Email": userinfo["Email"]}), 200
                else:
                    return jsonify("Cant find temppass field"), 401

            else:
                print("Username or password is incorrect")
                return jsonify("Username or password is incorrect"), 401
        except Exception as e:
            print(str(e))
            print("in exception")
            return jsonify("cant connect" + str(e)), 500

