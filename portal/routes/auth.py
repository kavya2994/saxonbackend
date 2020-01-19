import jwt
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from ..encryption import Encryption
from ..models.users import Users


auth_blueprint = Blueprint('auth_blueprint', __name__, template_folder='templates')

@auth_blueprint.route('/checktoken', methods=['POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
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
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type'])
def login():
    if request.method == "POST" or request.method == "OPTIONS":
        print(request.headers)
        print(request.get_data())
        print(request.data)
        print(request.remote_addr)
        print("####################")
        try:
            data = json.loads(str(request.data, encoding='utf-8'))
            print(data)
            user = data['username']
            password = data["password"]
            # userinfo = db1.collection("users").document(user).get().to_dict()
            userinfo = Users.query.filter_by(Username=user).first()
            encrypt_password = Encryption().encrypt(password)
            print(userinfo)
            # print(list(userinfo.keys()))
            # print(userinfo["password"])
            if userinfo != None and userinfo["password"] == encrypt_password and str(userinfo["status"]).lower() == "active":
                if "temppass" in userinfo.keys():
                    # print(request.form)
                    name = userinfo["displayname"]
                    role = userinfo["role"]
                    exp = datetime.utcnow()
                    if userinfo["role"] == "reviewermanager":
                        exp += timedelta(hours=1, minutes=30)
                    else:
                        # exp += timedelta(minutes=30)
                        exp += timedelta(hours=1, minutes=30)
                    encode = jwt.encode({'user': user, 'exp': exp, 'ip': data["ip"], "role": userinfo["role"]},
                                        'secret', algorithm="HS256")
                    return jsonify({"fusername": "test@test.com", "fpass": "test001", "id": user, "username": user,
                                    "firstName": name, "lastname": name, "role": role,
                                    "temppass": userinfo["temppass"],
                                    'token': str(encode.decode('utf-8')),
                                    "securityQuestion": ("securityQuestion" in userinfo.keys()),
                                    "email": userinfo["email"]}), 200
                else:
                    return jsonify("Cant find temppass field"), 401

            else:
                print("Username or password is incorrect")
                return jsonify("Username or password is incorrect"), 401
        except Exception as e:
            print(str(e))
            print("in exception")
            return jsonify("cant connect" + str(e)), 500

