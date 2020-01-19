import os
import random
import shutil
import string
import threading
import time
import zipfile
import threading
from flask import Flask, render_template, url_for, request, redirect, Response, session, flash, send_from_directory, \
    send_file, abort, jsonify, logging, make_response
from flask_cors import CORS, cross_origin
import json
import firebase_admin
from firebase_admin import db, credentials, auth, firestore
import jwt
from datetime import datetime, timedelta

import xlrd
from xlutils.copy import copy
from gevent.pywsgi import WSGIServer
from werkzeug.utils import secure_filename

from encrypt_pass import Encryption
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(verbose=True)

DATA_DIR = os.getenv("DATA_DIR", default="E:\\Saxons_folders")
SECRET_DIR = os.getenv("SECRET_DIR", default="secret")
CONNECTION_STRING = os.getenv("CONNECTION_STRING")

cred = credentials.Certificate(os.path.join(SECRET_DIR, "portals-2edf2-firebase-adminsdk-aljih-9a4318b0c8.json"))
firebase_admin.initialize_app(cred)
db1 = firestore.client()

app = Flask(__name__)
CORS(app, resources={"/login1": {
    "origins": ['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
                'http://192.168.2.146:812']},
                     "/checktoken": {"origins": ['https://angularproject-5c26e.firebaseapp.com',
                                                 'http://localhost:4200', 'http://183.82.0.186:812',
                                                 'http://192.168.2.146:812']},
                     "/initiate_enrollment": {"origins": ['https://angularproject-5c26e.firebaseapp.com',
                                                          'http://localhost:4200', 'http://183.82.0.186:812',
                                                          'http://192.168.2.146:812']},
                     "/enrollment": {"origins": ['https://angularproject-5c26e.firebaseapp.com',
                                                 'http://localhost:4200', 'http://183.82.0.186:812',
                                                 'http://192.168.2.146:812']}
                     })
enc = Encryption()


# logging.getLogger('flask_cors').level = logging.DEBUG
@app.route('/')
def start():
    return render_template("start.html")


@app.route('/file', methods=["POST"])
def files_():
    if 'file' in request.files:
        file = request.files['file']
        print("hello")
        filename = secure_filename(file.filename)
        print(filename)

        file.save(os.path.join(filename))
        return "success", 200


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    print(request.headers)
    return jsonify({'ip': request.environ['REMOTE_ADDR']}), 200


@app.route('/checktoken', methods=['POST', 'OPTIONS'])
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


@app.route('/login1', methods=['POST', 'OPTIONS'])
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
            userinfo = db1.collection("users").document(user).get().to_dict()
            encrypt_password = Encryption().encrypt(password)
            print(userinfo)
            # print(list(userinfo.keys()))
            # print(userinfo["password"])
            if userinfo["password"] == encrypt_password and str(userinfo["status"]).lower() == "active":
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


@app.route('/createuser', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
def create_user():
    if request.method == "POST":
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
            try:
                auth = request.headers["Authorization"]
                auth1 = jwt.decode(auth, key='secret')
                if auth1["role"] == "admin" and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
                    data = json.loads(str(request.data, encoding='utf-8'))
                    username = data["username"]
                    displayname = data["displayname"]
                    email = data["email"]
                    role = data["role"]
                    session_expiry = data["session_expiry"]
                    password = randomStringwithDigitsAndSymbols(10)
                    enc_pass = enc.encrypt(password)
                    userexist = db1.collection("users").document(username).get().to_dict()
                    if userexist is None:
                        db1.collection("users").document(username).update({"email": email,
                                                                           "password": enc_pass,
                                                                           "role": role,
                                                                           "status": "active",
                                                                           "temppass": True,
                                                                           "username": username,
                                                                           "displayname": displayname,
                                                                           "sessionExpiry": session_expiry,
                                                                           "userCreatedTime": datetime.utcnow()
                                                                           })
                        msg_text = MIMEText('<p>Dear %s</p>'
                                            '<p>Your account is created please use this password %s to log in</p>'
                                            % (displayname, password))
                        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
                        # smtpObj.set_debuglevel(1)
                        password = randomStringwithDigitsAndSymbols()
                        pass_encypt = Encryption().encrypt(password)
                        msg = MIMEMultipart()
                        msg['subject'] = "Welcome to Pension Management portal"
                        msg['from'] = "venkatesh"
                        msg['to'] = "venkatesh"
                        msg.attach(msg_text)
                        smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                        smtpObj.sendmail("venkateshvyyerram@gmail.com", email, msg.as_string())
                        return jsonify({"result": "Success"}), 200
                    else:
                        return jsonify({"error": "Username already exists"}), 409
            except jwt.DecodeError:
                return jsonify({"error": "Not Authorized"}), 401
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Not Authorized"}), 401
            except Exception as e:
                print(str(e))
                return jsonify({"error": "Not Authorized"}), 401
        else:
            return jsonify({"error": "Not Authorized"}), 401


# @app.route('/sendnotification', methods=['GET', 'POST', 'OPTIONS'])
# @cross_origin(origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812', 'http://192.168.2.146:812'], allow_headers=['Content-Type', 'application/json'])
# def notification():
#     if request.method == "POST":
#         try:
#             print(request.headers["Authorization"])
#             data = json.loads(str(request.data, encoding='utf-8'))
#             print(data)
#
#         except KeyError as e:
#             print(str(e))
#
#     return "", 204

@app.route('/checkuserexists', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'User', 'Ipaddress'])
def check_user():
    if request.method == "POST":
        data = json.loads(str(request.data, encoding='utf-8'))
        username = data["username"]
        user_details = db1.collection("users").document(username).get().to_dict()
        if user_details is not None:
            return jsonify({
                "result": True
            }), 200
        else:
            return jsonify({"error": "user doesn't exist"}), 400


@app.route('/securityquestion', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type'])
def get_security_question():
    if request.method == "POST":
        data = json.loads(str(request.data, encoding='utf-8'))
        username = data["username"]
        user_details = db1.collection("users").document(username).get().to_dict()
        if user_details is not None:
            sec_question = user_details["securityQuestion"]
            print(sec_question)
            question = db1.collection("securityQuestions").where("id", "==", str(sec_question)).stream()

            question_ = ""

            for doc in question:
                print(doc)
                question_ = doc.to_dict()["question"]
                print(question_)

            return jsonify({"question": question_, "email": user_details["email"]}), 200
        else:
            return jsonify({"error": "user doesn't exist"}), 400
    else:
        return "Not Found", 404


@app.route('/setsecurityquestion', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200',
            'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def security_question():
    if request.method == "POST":
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
            try:
                auth = request.headers["Authorization"]
                auth = jwt.decode(auth, key='secret')
                data = json.loads(str(request.data, encoding='utf-8'))
                username = data["username"]
                securityquestion = data["securityQuestion"]
                answer = data["answer"]
                db1.collection("users").document(username).update({"securityQuestion": securityquestion,
                                                                   "answer": enc.encrypt(answer)})
                return jsonify({"result": "success"}), 200
            except KeyError as e:
                print(str(e))
                return jsonify({"error": "Bad request"}), 400
            except jwt.DecodeError:
                return jsonify({"error": "Not Authorized"}), 401
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "please refresh the token"}), 401
        else:
            return jsonify({"error": "Not Authorized"}), 401


@app.route('/changepass', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def change():
    if request.method == "POST":
        try:
            print(request.headers)
            print(request.data)
            data = json.loads(str(request.data, encoding='utf-8'))
            # token = request.headers["Authorization"]
            if 'Authorization' in request.headers.keys() and token_verify(request.headers["Authorization"],
                                                                          request.headers["User"],
                                                                          request.headers["Ipaddress"]):

                username = data["username"]
                old_pass = data["old_password"]
                new_pass = data["new_password"]
                if username is not None:
                    userinfo = db1.collection("users").document(username).get().to_dict()
                    if userinfo["password"] == enc.encrypt(old_pass):
                        pass_encoded = enc.encrypt(new_pass)
                        db1.collection("users").document(username).update({"password": pass_encoded, "temppass": False})
                        return jsonify({"result": "Password changed successfully"}), 200
                    else:
                        return jsonify({"error": "Password not match"}), 401
                else:
                    return jsonify({})
            else:
                return jsonify({"error": "Not Authorized"}), 401
        except KeyError as e:
            if str(e).__contains__("Authorization"):
                return jsonify({"error": "Not Authorized"}), 401
            else:
                print(str(e))
                return {"error": "Irrelevant data"}, 417


@app.route('/login_cred', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type'])
def login_cred_mail():
    if request.method == "POST":
        print(request.data)
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        type = data["role"]
        memberid = data["username"]
        url = data["url"] + type
        name = data["name"]
        username = data["user"]
        email = data["email"]
        msgtext1 = ""
        node = type
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        # smtpObj.set_debuglevel(1)
        password = randomStringwithDigitsAndSymbols()
        pass_encypt = enc.encrypt(password)
        msg = MIMEMultipart()
        msg['subject'] = "Welcome to Pension Management portal"
        msg['from'] = "venkatesh"
        msg['to'] = name
        if type == "member":
            msgtext1 = MIMEText(
                '<style>td:firstchild{color:red;}</style><p>Dear %s,</p><p>We would like to take this opportunity to '
                'welcome '
                'you to the plan. Please note your account number is <strong>%s</strong>.'
                ' I\'ve attached a copy of your confirmation of '
                'enrollment into our plan. In addition, I\'ve included your login details to our member '
                'portal.</p><p>To '
                'access your online account, please see details '
                'below.</p><table><tr><td>URL</td><td>:</td><td>%s</td></tr><tr><td>User '
                'Name</td><td>:</td><td>%s</td></tr><tr><td>Password</td><td>:</td><td>%s</td></tr></table>' % (
                    name, memberid, url, username, password
                ), 'html')
        elif type == "employer":
            msgtext1 = MIMEText(
                '<p>Dear %s,</p><p>We would like to take this opportunity to '
                'welcome '
                'you to the plan. Please note your account number is <strong>%s</strong>. I\'ve attached a copy of your confirmation of '
                'enrollment into our plan. In addition, I\'ve included your login details to our member '
                'portal which will allow you to complete the following: </p><p>Enroll new employees and retrieve member numbers <br/>'
                'Terminate ex-employees<br/>Download your latest contribution sheet<br/>Access monthly '
                'reports</p><p>To access your online account, please see details '
                'below.</p><table><tr><td>URL</td><td>:</td><td>%s</td></tr><tr><td>User '
                'Name</td><td>:</td><td>%s</td></tr><tr><td>Password</td><td>:</td><td>%s</td></tr></table>' % (
                    name, memberid, url, username, password
                ), 'html')
        elif type == "reviewer":
            msgtext1 = MIMEText(
                '<p>Dear %s,</p><p>We would like to take this opportunity to '
                'welcome '
                'you to the plan. Please note your account number is <strong>%s</strong>. I\'ve attached a copy of '
                'your confirmation of '
                'enrollment into our plan. In addition, I\'ve included your login details to our member '
                'portal which will allow you to complete the following: </p><p>Enroll new employees and retrieve '
                'member numbers<br/> '
                'Terminate ex-employees<br/>Download your latest contribution sheet<br/>Access monthly '
                'reports</p><p>To access your online account, please see details '
                'below.</p><table><tr><td>URL</td><td>:</td><td>%s</td></tr><tr><td>User '
                'Name</td><td>:</td><td>%s</td></tr><tr><td>Password</td><td>:</td><td>%s</td></tr></table>' % (
                    name, memberid, url, username, password
                ), 'html')
        elif type == "admin":
            msgtext1 = MIMEText(
                '<p>Dear %s,</p><p>We would like to take this opportunity to '
                'welcome '
                'you to the plan. Please note your account number is <strong>%s</strong>. I\'ve attached a copy of your confirmation of '
                'enrollment into our plan. In addition, I\'ve included your login details to our member '
                'portal.</p><p>To '
                'access your online account, please see details '
                'below.</p><table><tr><td>URL</td><td>:</td><td>%s</td></tr><tr><td>User '
                'Name</td><td>:</td><td>%s</td></tr><tr><td>Password</td><td>:</td><td>%s</td></tr></table>' % (
                    name, memberid, url, username, password
                ), 'html')
        try:
            msg.attach(msgtext1)
            smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
            smtpObj.sendmail("venkateshvyyerram@gmail.com", email, msg.as_string())
            return jsonify({"result": "Success"}), 200
        except Exception as e:
            print(str(e))
            return jsonify({"error": "sorry"}), 500


@app.route("/resetpass", methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def reset_pass_():
    if request.method == "POST":
        print(request.data)
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        change_pass = False
        request_type = data["request_type"]
        id = data["username"]
        mail = data["email"]
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        msg = MIMEMultipart()
        msg['subject'] = "Password Reset"
        msg['from'] = "venkatesh"
        msg['to'] = "venkatesh"

        if 'Authorization' in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers[
                                                                          "User"]) and request_type == "admin":
            change_pass = True
        elif request_type == "securityquestion":
            answer = data["answer"]
            userdata = db1.collection("users").document(id).get().to_dict()
            if userdata["answer"] == enc.encrypt(answer):
                change_pass = True
        elif request_type == "email":
            userdata = db1.collection("users").document(id).get().to_dict()
            print(userdata)
            if userdata is not None and userdata["email"] == mail:
                change_pass = True

        if change_pass:
            try:
                password = randomStringwithDigitsAndSymbols()
                pass_encypt = enc.encrypt(password)
                msgtext = MIMEText('<p>Your password has been reset. The temporary password is: %s</p>'
                                   '<p>Please log into your system as soon as possible to set your new password.</p>'
                                   % password, 'html')
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                db1.collection('users').document(id).update({"password": pass_encypt, "temppass": True})
                smtpObj.sendmail("venkateshvyyerram@gmail.com", mail, msg.as_string())
                return jsonify({"result": "Success"}), 200
            except Exception as e:
                print(str(e))
                return jsonify({"error": "sorry"}), 500


@app.route("/initiate_enrollment", methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def send_enrollment_form():
    if request.method == "POST":
        print(request.headers)
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                auth = request.headers["Authorization"]
                auth = jwt.decode(auth, key='secret')
                if auth["role"] == "employer":
                    data = json.loads(str(request.get_data(), encoding='utf-8'))
                    member_email = data["email"]
                    employer_id = data["employernumber"]
                    # employer_name = data["employername"]
                    member_name = data["memberfirstName"]
                    # form_type = data["formType"]
                    employer_comments = data["comments"]
                    print(data)

                    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
                    msg = MIMEMultipart()
                    msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg['from'] = "venkatesh"
                    msg['to'] = member_name
                    employernumber = employer_id

                    try:
                        data["formCreatedDate"] = datetime.utcnow()
                        if str(employer_id)[-2:].__contains__("HR"):
                            employernumber = str(employer_id)[:-2]
                        print(employernumber)
                        myform_enroll = db1.collection("myforms").add(data)
                        token_data = db1.collection("Tokens").add(
                            {"id": myform_enroll[1].id, "initiatedBy": employer_id, "tokenStatus": "active",
                             # "tokenType": "enrollment",
                             "formCreatedDate": datetime.utcnow(),
                             "pendingFrom": "member",
                             "formType": "Enrollment",
                             "status": "pending",
                             "employernumber": employernumber,
                             "memberfirstName": member_name})
                        token = token_data[1].id
                        msgtext = MIMEText(
                            '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>'
                            '<p>Dear %s</p>'
                            '<p>Please click here. Otherwise, cut and paste the link below into a browser, fill in the '
                            'required information, and when you are done hit the submit button to start your enrollment '
                            'into the plan.</p><p>-----------------------------------------</p>'
                            '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
                            '<p>To learn more about the Silver Thatch Pension Plan,'
                            ' click here to review our members handbook. </p>' % (member_name, token), 'html')
                        msg.attach(msgtext)
                        smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                        smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                        return jsonify({"result": "Success"}), 200
                    except Exception as e:
                        return jsonify({"error": "Something wrong happened"}), 500
                else:
                    print("role is not employer")
                    return jsonify({"error": "UnAuthorised"}), 401

            except Exception as e:
                print(str(e))
                return jsonify({"error": "UnAuthorised"}), 401
        else:
            print("role is not employer")
            return jsonify({"error": "UnAuthorised"}), 401


@app.route("/delete_enrollment_file", methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def deleteenrollmentfile():
    if request.method == "POST":
        base_path = os.path.join(DATA_DIR, 'Employers')
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        employer = data["employerid"]
        path = data["path"]
        base_path = os.path.join(base_path, employer, path)
        if os.path.exists(base_path) and os.path.isfile(base_path):
            try:
                os.remove(base_path)
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                return jsonify({"error": "Can't delete the file"}), 500
        else:
            return jsonify({"error": "Bad request"}), 400


@app.route("/save_enrollment", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def save_enrollment():
    if request.method == "POST":
        member_name = request.form.get("membername")
        token = request.form.get("tokenID")
        member_email = request.form.get("email")
        type = request.form.get("request_type")
        employer_id = request.form.get("employerusername")
        path = DATA_DIR
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if type == "member_submission":
            msg['subject'] = "Your Enrollment has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment was submitted on %s. '
                               'You will receive notification once your form has been processed</p>' % (
                                   member_name, datetime.utcnow().strftime("%Y-%m-%d")),
                               'html')
            member_token_data = db1.collection("Tokens").document(token).get().to_dict()
            new_token_data = member_token_data
            new_token_data["pendingFrom"] = "employer"
            new_token_data["oldToken"] = token
            new_token_data["status"] = "pending"
            new_token_data["tokenStatus"] = "active"
            db1.collection("Tokens").document(token).update({"tokenStatus": "inactive", "status": "submitted"})
            db1.collection("myforms").document(member_token_data["id"]).update({"pendingFrom": "employer"})
            new_token = db1.collection("Tokens").add(new_token_data)
            print(new_token[1].id)
            try:
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + "/n" + str(e) + "/n")
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "save_formData":
            print("savingformdata")
            print(request.form["enrollmentFormData"])
            enroll_form_data = json.loads(request.form.get("enrollmentFormData"))
            if 'file' in request.files:
                print("hello")
                file = request.files["file"]
                filename = secure_filename(file.filename)
                print(filename)
                path = os.path.join(path, 'Employers')
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, employer_id)
                print(employer_id)
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, "enrollment")
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, request.form["tokenID"])
                if not os.path.exists(path):
                    os.mkdir(path)
                file.save(os.path.join(path, filename))
                enroll_form_data["filename"] = filename

            # getting id from tokens
            print(token)
            token_data = db1.collection("Tokens").document(token).get().to_dict()
            print(token_data)
            print(request.form["enrollmentFormData"])
            print(token_data["id"])
            dob = enroll_form_data["dob"]
            formcreateddate = enroll_form_data["formCreatedDate"]
            if not dob == "":
                enroll_form_data["dob"] = datetime.strptime(str(dob).split("T")[0], "%Y-%m-%d")
            # print(enroll_form_data["memberLastName"])
            if not formcreateddate == "":
                str(formcreateddate).split(" ")
            db1.collection("myforms").document(token_data["id"]).update(enroll_form_data)
            return jsonify({"result": "success"}), 200
        elif type == "employer_submission":
            enroll_form_data = json.loads(request.form.get("enrollmentFormData"))
            print(enroll_form_data)
            if 'file' in request.files:
                print("hello")
                file = request.files["file"]
                filename = secure_filename(file.filename)
                print(filename)
                path = os.path.join(path, "Employers/")
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, employer_id)
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, "enrollment")
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, request.form["tokenID"])
                if not os.path.exists(path):
                    os.mkdir(path)
                file.save(os.path.join(path, filename))
                enroll_form_data["filename"] = filename
            enroll_form_data["pendingFrom"] = "reviewermanager"
            token_data = db1.collection("Tokens").document(token).get().to_dict()
            db1.collection("Tokens").document(token).update({"pendingFrom": "reviewermanager"})
            db1.collection("myforms").document(token_data["id"]).update(enroll_form_data)
            return jsonify({"result": "success"}), 200


@app.route("/enrollment", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def send_enrollment():
    if request.method == "GET":
        token = request.args["token"]
        tokendata = db1.collection("Tokens").document(token).get().to_dict()
        print(tokendata)
        if tokendata is not None and "id" in tokendata.keys():
            formdata = db1.collection("myforms").document(tokendata["id"]).get().to_dict()
            print(formdata)
            return jsonify({"result": formdata}), 200
        else:
            return jsonify({"error": "Bad Request"}), 400
    if request.method == "POST":
        print(request.get_data())
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        print(data)
        member_name = data["membername"]
        token = data["tokenID"]
        member_email = data["email"]
        type = data["request_type"]
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if type == "remainder":
            notify = data["notify"]
            try:
                token_data = db1.collection("Tokens").document(token).get().to_dict()
                form_data = db1.collection("myforms").document(token_data["id"]).get().to_dict()
                if "formCreatedDate" in form_data.keys():
                    # init_time = datetime.strptime(form_data["formCreatedDate"], "%d%m%Y %H:%M:%S.%f")
                    # time = (datetime.utcnow() - form_data["formCreatedDate"]).days
                    msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                                       ' Please do not reply to this message. **</p>'
                                       '<p>Dear %s</p>'
                                       '<p>Please click here. Otherwise, '
                                       'cut and paste the link below into a browser, fill in the '
                                       'required information, and when you are done'
                                       ' hit the submit button to start your enrollment '
                                       'into the plan.</p>'
                                       '<p>-----------------------------------------</p>'
                                       '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
                                       '<p>To learn more about the Silver Thatch Pension Plan,'
                                       ' click here to review our members handbook. </p>' % (member_name, token),
                                       'html')
                    # if time == 3:
                    #     notify = True
                    # elif time > 3:
                    #     if "notifytime" in form_data:
                    #         # notify_time = datetime.strptime(form_data["notifytime"], "%d%m%Y %H:%M:%S.%f")
                    #         time_days = (datetime.utcnow() - form_data["notifytime"]).days
                    #         if time_days == 3:
                    #             notify = True
                    if notify:
                        msg.attach(msgtext)
                        db1.collection("myforms").document(token_data["id"]).update({"notifytime": datetime.utcnow()})
                        smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                        smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                        return jsonify({"result": "success"}), 200

            except KeyError as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500

        elif type == "approval_confirmation":
            msg['subject'] = "Your Enrollment has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment has been processed </p>' % (
                                   member_name),
                               'html')
            db1.collection("Tokens").document(token).update({"status": "approved"})
            try:
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "rejected":
            msg['subject'] = "Your Enrollment has been rejected"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment has been rejected </p>'
                               '<p>Please click here. Otherwise, cut and paste the link below into a browser, '
                               'fill in the required information, and when you are done hit the submit button to '
                               'start your enrollment into the plan.</p>'
                               '<p>%s</p>'
                               '<p>-----------------------------------</p>'
                               '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
                               '<p>To learn more about the Silver Thatch Pension '
                               'Plan, click here to review our members handbook. </p>' % (
                                   member_name, data["comments"], token),
                               'html')
            try:
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500


@app.route("/initiate_termination", methods=['POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def send_termination_form():
    if request.method == "POST":
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key='secret')
                if auth1["role"] == "employer":
                    data = json.loads(str(request.get_data(), encoding='utf-8'))
                    # member_email = data["email"]
                    # employer_id = data["id"]
                    # member_name = data["membername"]
                    # employer_comments = data["comments"]
                    member_email = data["email"]
                    employer_id = data["employernumber"]
                    employer_name = data["employername"]
                    member_name = data["memberfirstName"]
                    form_type = data["formType"]
                    employer_comments = data["comments"]
                    employernumber = employer_id
                    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
                    msg = MIMEMultipart()
                    msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg['from'] = "venkatesh"
                    msg['to'] = member_name

                    try:
                        data["formCreatedDate"] = datetime.utcnow()
                        if str(employer_id)[-2:].__contains__("HR"):
                            employernumber = str(employer_id)[:-2]
                        print(employernumber)
                        myform_enroll = db1.collection("myforms").add(data)
                        token_data = db1.collection("Tokens").add(
                            {"id": myform_enroll[1].id, "initiatedBy": employer_id, "tokenStatus": "active",
                             # "tokenType": "enrollment",
                             "formCreatedDate": datetime.utcnow(),
                             "pendingFrom": "member",
                             "formType": "termination",
                             "status": "pending",
                             "employernumber": employernumber,
                             "memberfirstName": member_name
                             })
                        token = token_data[1].id
                        msgtext = MIMEText(
                            '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>'
                            '<p>Dear %s</p>'
                            '<p>In an effort to keep you connected with your Silver Thatch Pension after you leave your '
                            'current position, please click here or copy the link below into a browser to complete the '
                            'termination of employment form. This form notifies us that you are no longer employed with '
                            'your current employer and allows Silver Thatch Pensions to stay in touch with you in regards '
                            'to your pension. </p><p>-----------------------------------------</p> '
                            '<p>https://183.82.0.186:812/terminationform/%s</p>'
                            '<p>To learn more about the Silver Thatch Pension Plan,'
                            ' click here to review our members handbook. </p>' % (member_name, token), 'html')
                        msg.attach(msgtext)
                        smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                        smtpObj.set_debuglevel(2)
                        smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                        return jsonify({"result": "Success"}), 200
                    except Exception as e:
                        print(str(e))
                        file = open("log.txt", "a+")
                        file.writelines(str(datetime.utcnow()) + str(e))
                        file.close()
                        return jsonify({"error": "Something wrong happened"}), 500
            except Exception as e:
                print(str(e))
                return jsonify({"error": "Un Authorised"}), 401


@app.route("/termination", methods=['POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def send_termination():
    if request.method == "POST":
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        member_name = data["membername"]
        member_email = data["email"]
        type = data["request_type"]
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if type == "remainder":
            notify = data["notify"]
            token = data["tokenID"]
            try:
                msg['subject'] = "Please complete your Silver Thatch Pensions Employment Termination Form"
                msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                                   ' Please do not reply to this message. **</p>'
                                   '<p>Dear %s</p>'
                                   '<p>In an effort to keep you connected with your Silver Thatch Pension '
                                   'after you leave your current position, please click here or copy the link '
                                   'below into a browser to complete the termination of employment form. This '
                                   'form notifies us that you are no longer employed with your current '
                                   'employer and allows Silver Thatch Pensions to stay in touch with you in '
                                   'regards to your pension. </p> '
                                   '<p>-----------------------------------------</p>'
                                   '<p>https://183.82.0.186:812/terminationform/%s</p>'
                                   '<p>To learn more about the Silver Thatch Pension Plan,'
                                   ' click here to review our members handbook. </p>' % (member_name, token),
                                   'html')

                if notify:
                    msg.attach(msgtext)
                    token_data = db1.collection("Tokens").document(token).get().to_dict()
                    db1.collection("myforms").document(token_data["id"]).update({
                        "notifytime": datetime.utcnow()
                    })
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200

            except KeyError as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500
        elif type == "submission_confirmation":
            msg['subject'] = "Your Termination form has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your termination was submitted on %s. '
                               'You will receive notification once your form has been processed</p>' % (
                                   member_name, datetime.utcnow().strftime("%Y-%m-%d")),
                               'html')
            try:
                if not msgtext == "":
                    msg.attach(msgtext)
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200
                else:
                    return "Invalid request", 417
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "approval_confirmation":
            msg['subject'] = "Your Termination has been approved"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your termination has been processed </p>' % (
                                   member_name),
                               'html')
            try:
                if not msgtext == "":
                    msg.attach(msgtext)
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200
                else:
                    return "Invalid request", 417
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "rejected":
            token = data["token"]
            msg['subject'] = "Your termination has been rejected"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Termination has been rejected </p>'
                               '<p>Please click here. Otherwise, cut and paste the link below into a browser, '
                               'fill in the required information, and when you are done hit the submit button to '
                               'start your termination into the plan.</p>'
                               '<p>-----------------------------------------------------</p>'
                               '<p>https://183.82.0.186:812/terminationform/%s </p>'
                               '<p>To learn more about the Silver Thatch Pension '
                               'Plan, click here to review our members handbook. </p>' % (
                                   member_name, token),
                               'html')
            try:
                if not msgtext == "":
                    msg.attach(msgtext)
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200
                else:
                    return "Invalid request", 417
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500


# @app.route("/updatedetails", methods=['POST', 'OPTIONS'])
# @cross_origin(origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812', 'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'user', 'ipaddress'])
# def update_details():
#     if request.method == "POST":
#         data = json.loads(str(request.get_data(), encoding='utf-8'))
#         member_name = data["name"]
#         member_email = data["email"]
#         type = data["request_type"]
#         msgtext = ""
#         msg = MIMEMultipart()
#         msg['from'] = "venkatesh"
#         msg['to'] = member_name
#         smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
#         if type == "member":
#             msg['subject'] = " Your Member update details form has been submitted"
#             msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
#                                ' Please do not reply to this message. **</p>'
#                                '<p>Dear %s</p>'
#                                '<p>Your member updated details was submitted on %s. '
#                                'You will receive notification once your form has been processed. </p>' % (
#                                    member_name, datetime.utcnow().strftime("%Y-%m-%d")),
#                                'html')
#         elif type == "beneficiary":
#             msg['subject'] = "Your Beneficiary update details form has been submitted"
#             msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
#                                ' Please do not reply to this message. **</p>'
#                                '<p>Dear %s</p>'
#                                '<p>Your beneficiary updated details was submitted on %s. '
#                                'You will receive notification once your form has been processed. </p>' % (
#                                    member_name, datetime.utcnow().strftime("%Y-%m-%d")),
#                                'html')
#         try:
#             if not msgtext == "":
#                 msg.attach(msgtext)
#                 smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
#                 smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
#                 return "OK", 200
#             else:
#                 return "Invalid request", 417
#         except Exception as e:
#             print(str(e))
#             file = open("log.txt", "a+")
#             file.writelines(str(datetime.utcnow()) + str(e))
#             file.close()
#             return jsonify({"error": "Something wrong happened while sending the mail"}), 500


@app.route("/file_explorer", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer():
    if request.method == "POST":
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                print('post dataa')
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key='secret')
                data = json.loads(str(request.data, encoding='utf-8'))

                path = os.path.join(DATA_DIR, data["request_folder"])
                folders = {}
                object_to_send = []
                id = 1
                # r=root, d=directories, f = files
                for r, d, f in os.walk(path):
                    # folders[parent] = {}
                    for folder in d:
                        p = r.split("\\")
                        parent = p[len(p) - 1]
                        if parent == '' or parent == data["request_folder"]:
                            parent = 'root'
                            # print(r.split("\\"))
                            if parent not in folders.keys():
                                folders[parent] = {}
                            object_to_send.append({"id": id, "name": folder, "isFolder": True,
                                                   "parent": 'root',
                                                   "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                 time.localtime(os.path.getmtime(
                                                                                     os.path.join(r, folder))))})
                            folders[parent][folder] = id
                            id += 1
                        else:
                            if parent not in folders.keys():
                                folders[parent] = {}
                                # print(folders)
                            if folder not in folders[parent]:
                                actual_parent = p[len(p) - 2]
                                if actual_parent == data["request_folder"]:
                                    actual_parent = 'root'
                                object_to_send.append({"id": id, "name": folder, "isFolder": True,
                                                       "parent": folders[actual_parent][parent],
                                                       "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                     time.localtime(os.path.getmtime(
                                                                                         os.path.join(r, folder))))})
                                folders[parent][folder] = id
                                id += 1
                    # print(folders)
                    for file in f:
                        # files.append(os.path.join(r, file))
                        p = r.split("\\")
                        parent = p[len(p) - 1]
                        if parent == '':
                            parent = 'root'
                            # print(r.split("\\"))
                            object_to_send.append({"id": id, "name": file, "isFolder": False, "parent": 'root',
                                                   "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                 time.localtime(os.path.getmtime(
                                                                                     os.path.join(r, file))))})
                            id += 1
                        else:

                            # print(p)
                            folder = p[len(p) - 2]
                            if folder == data["request_folder"]:
                                folder = 'root'
                            # print(parent)
                            # print(folder)
                            object_to_send.append(
                                {"id": id, "name": file, "isFolder": False, "parent": folders[folder][parent],
                                 "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                               time.localtime(
                                                                   os.path.getmtime(os.path.join(r, file))))})
                            id += 1
                print(object_to_send)
                return jsonify(object_to_send), 200
            except jwt.DecodeError:
                print("decode error")
                return jsonify({"error": "Un Authorised"}), 401
            except jwt.ExpiredSignatureError:
                print("sign")
                return jsonify({"error": "Un Authorised"}), 401
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500
        else:
            return jsonify({"error": "Un Authorised"}), 401
    if request.method == 'GET':
        auth1 = request.headers["Authorization"]
        auth1 = jwt.decode(auth1, key='secret')
        print(request+" get requesttt")
        data = json.loads(str(request.data, encoding='utf-8'))
        return send_file(os.path.join(DATA_DIR, data["request_folder"])), 200


@app.route("/download_file", methods=["POST", "OPTIONS"])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def download():
    if request.method == "POST":
        root = DATA_DIR
        data = json.loads(str(request.data, encoding='utf-8'))
        print("-------------")
        print(data)
        root = os.path.join(root, data["request_folder"])
        path_ = os.path.join(DATA_DIR, data["request_folder"])
        paths = list(data["path"])
        print(paths)
        return send_file(os.path.join(path_, paths[0])), 200


@app.route("/file_explorer_open", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer_open():
    if request.method == "POST":
        if 'Authorization' in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            root = DATA_DIR
            data = json.loads(str(request.data, encoding='utf-8'))
            print("-------------")
            print(data)
            root = os.path.join(root, data["request_folder"])
            path_ = os.path.join(DATA_DIR, data["request_folder"])
            paths = list(data["path"])
            print(paths)

            # if not len(paths) == 1:
            time = datetime.utcnow().strftime("%d%m%Y%H%M%S%f")
            zip_file = zipfile.ZipFile(str(time) + ".zip", 'w')
            with zip_file:
                for path in paths:
                    finalpath = root + path
                    print(finalpath)
                    if os.path.isfile(finalpath):
                        zip_file.write(finalpath)
                    elif os.path.isdir(finalpath):
                        for r, d, f in os.walk(finalpath):
                            for folders in d:
                                zip_file.write(os.path.join(r, folders))
                            for files in f:
                                zip_file.write(os.path.join(r, files))
                    zip_file.close()
                    threading.Thread(target=delete_excel, args=(str(time) + '.zip',)).start()
                    return send_file(str(time) + '.zip', as_attachment=str(time) + '.zip')
        else:
            return jsonify({"error": "Not Authorized"}), 401
        # elif len(paths) == 1:
        #     folder = str(path_ + paths[0]).split("/")
        #     if os.path.isdir(path_ + paths[0]):
        #         return send_file(
        #             shutil.make_archive(folder[len(folder) - 1], 'zip', path_ + paths[0])
        #             , folder[len(folder) - 1]), 200
        #     elif os.path.isfile(path_ + paths[0]):
        #         return send_file(path_ + paths[0]), 200
        #     else:
        #         jsonify({"error": "No file found"}), 404
    if request.method == 'GET':
        print(request.headers)
        path = request.args.get('path')
        print(path)
        return send_file(os.path.join(DATA_DIR, path)), 200


@app.route("/file_explorer_operation", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer_operation():
    if request.method == "POST":
        print(request.headers)
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key='secret')
                path = DATA_DIR
                file = request.files['file']
                print("----------------")
                print(request.form["request_type"])
                print("----------------")
                # print(file.filename)
                if request.form["request_type"] == "contribution":
                    startdate = request.form["startDate"]
                    enddate = request.form["endDate"]
                    print(startdate)
                    start_date = datetime.strptime(startdate, "%a %b %d %Y")
                    end_date = datetime.strptime(enddate, "%a %b %d %Y")
                    formtype = request.form["formType"]
                    userid = request.form["employerusername"]
                    employer = request.form["employer"]
                    path = os.path.join(root, "Employers")
                    if not os.path.exists(path):
                        os.mkdir(path)
                    path = os.path.join(path, userid)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    path = os.path.join(path, "contribution")
                    if not os.path.exists(path):
                        os.mkdir(path)
                    if 'file' in request.files:
                        print("hello")
                        filename = secure_filename(file.filename)
                        print(filename)
                        # filename = str(datetime.today().strftime("%Y%m%d %H%M%S.%f") + filename)
                        # myforms = db1.collection("myforms").add({"filename": filename, "startDate": start_date,
                        #                                          "endDate": end_date,
                        #                                          "employername": employer,
                        #                                          "employernumber": employer_id, "formType": formtype,
                        #                                          "formCreatedDate": datetime.utcnow(), "status": "pending",
                        #                                          "pendingFrom": "reviewer"})
                        # print(myforms[1].id)
                        token = db1.collection("Tokens").add({"initiatedBy": userid,
                                                              "startDate": start_date,
                                                              "endDate": end_date,
                                                              "employername": employer,
                                                              "employernumber": userid,
                                                              "formType": formtype,
                                                              "formCreatedDate": datetime.utcnow(),
                                                              "tokenStatus": "active",
                                                              "status": "pending",
                                                              "tokenType": "contribution",
                                                              "pendingFrom": "reviewer",
                                                              "filename": filename,
                                                              })

                        path = os.path.join(path, str(token[1].id))
                        if not os.path.exists(path):
                            os.mkdir(path)
                        file.save(os.path.join(path, filename))
                    else:
                        return jsonify({"error": "Bad request"}), 400

                    return jsonify({"result": "Success"}), 200
                elif request.form["request_type"] == "upload":
                    if 'file' in request.files:
                        print("hello")
                        try:
                            foldername = request.form["foldername"]
                            path = os.path.join(path, foldername)
                            filename = secure_filename(file.filename)
                            print(filename)
                            filename = str(datetime.today().strftime("%Y%m%d %H%M%S.%f") + filename)
                            # path += str(employer_id) + "/"
                            # if not os.path.exists(path):
                            #     os.mkdir(path)
                            file.save(os.path.join(path, filename))
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            jsonify({"error": "Bad Request"}), 400
                    return jsonify({"error": "No file found in the request"}), 400
            except Exception as e:
                print(str(e))
                return jsonify({"error": "Not Authorized"}), 401
        else:
            return jsonify({"error": "Not Authorized"}), 401

            # os.mkdir

        # return "hello", 200


@app.route("/file_explorer_operations", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer_operations():
    if request.method == "POST":
        print("---------------operations_headers---------------")
        print(request.headers)
        print("---------------operations_headers---------------")
        if "Authorization" in request.headers.keys():
            if token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"],
                            user=request.headers["User"]):
                try:
                    auth1 = request.headers["Authorization"]
                    auth1 = jwt.decode(auth1, key='secret')
                    data = json.loads(str(request.data, encoding='utf-8'))
                    operation = data["operation"]
                    print(operation)
                    path = os.path.join(DATA_DIR, data["request_folder"])
                    if operation == "move":

                        destination = os.path.join(path, data["destination"][0])
                        try:
                            for i in range(len(data["source"])):
                                source = os.path.join(path, data["source"][i])
                                shutil.move(source, destination)
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
                    elif operation == "copy":
                        destination = os.path.join(path, data["destination"][0])
                        try:
                            for i in range(len(data["source"])):
                                source = os.path.join(path, data["source"][i])
                                print(source)
                                print(destination)
                                len_of_source = len(source.split("/"))
                                if os.path.isdir(source):
                                    shutil.copytree(source, os.path.join(destination, source.split("/")[len_of_source - 1]))
                                elif os.path.isfile(source):
                                    shutil.copy(source, destination)
                                else:
                                    return jsonify({"error": "Something wrong happened"}), 500
                                return jsonify({"result": "Success"}), 200
                        except OSError as e:
                            if isinstance(e, WindowsError) and e.winerror == 183:
                                return jsonify({"error": "Cannot create a file when that file already exists"}), 500
                            elif isinstance(e, WindowsError) and e.winerror == 267:
                                return jsonify({"error": "Invalid file"}), 500
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
                    elif operation == "rename":
                        print(data)
                        result = []
                        try:
                            for i in range(len(list(data["source"]))):
                                source = os.path.join(path, data["source"][i])
                                destination = os.path.join(path, data["destination"][i])
                                os.rename(source, destination)
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
                    elif operation == "delete":
                        source = os.path.join(path, data["source"][0])
                        print(source)
                        try:
                            if os.path.isdir(source):
                                print("in dir")
                                shutil.rmtree(source)
                            elif os.path.isfile(source):
                                print("in file")
                                os.remove(source)
                            else:
                                return jsonify({"error": "Couldn't find the file or folder"}), 404
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
                    elif operation == "upload":
                        file = request.files['file']
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(path, filename))
                        return jsonify({"result": "Success"}), 200
                        # return send_file(os.path.join(path, filename))
                    elif operation == "createnewfolder":
                        folder_path = os.path.join(path, data["source"])
                        try:
                            os.mkdir(folder_path)
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Can't create folder"}), 500
                except Exception as e:
                    print(str(e))
                    return jsonify({"error": "bad request"}), 400
            else:
                return jsonify({"error": "Un Authorised"}), 401
        else:
            return jsonify({"error": "Un Authorised"}), 401
    return ""


@app.route("/buildexcel", methods=["POST", "OPTIONS"])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'user', 'ipaddress'])
def build_excel():
    if request.method == "POST":
        print(request.headers)
        print(request.data)

        data = json.loads(str(request.data, encoding='utf-8'))
        employer_username = data["username"]
        employer_name = data["employername"]

        current_datetime = datetime.today()
        rb = xlrd.open_workbook('Contributionex.xls', formatting_info=True)

        wb = copy(rb)

        w_sheet = wb.get_sheet(0)

        w_sheet.write(9, 1, employer_name)
        w_sheet.write(9, 5, employer_username)
        empuser = db1.collection("members").where("employers", "array_contains",
                                                  db1.collection("employers").document(employer_username)).stream()
        i = 16
        for doc in empuser:
            print(doc.to_dict())
            member_details = doc.to_dict()
            w_sheet.write(i, 0, member_details["member_id"])
            w_sheet.write(i, 1, member_details["displayname"])
            i += 1
        filename = current_datetime.strftime("%d%m%Y %H%M%S") + 'Contribution.xls'
        wb.save(filename)
        t = threading.Thread(target=delete_excel, args=(filename,))
        t.start()
        time.sleep(3)
        return send_file(filename), 200


def delete_excel(filename):
    time.sleep(5) #??!!
    print("deleting file" + filename)
    os.remove(filename)


def token_verify(token, user, ip):
    result = False
    # print(request.headers)
    try:
        # if "Authorization" in request.headers.keys():
        #     token = request.headers["Authorization"]
        # print(request.get_data())
        # data = json.loads(str(request.data, encoding='utf-8'))
        decoded = jwt.decode(token, key='secret')
        if decoded["user"] == user and decoded["ip"] == ip:
            result = True
    except jwt.DecodeError:
        print("decode error")
        result = False
    except jwt.ExpiredSignatureError:
        print("sign")
        result = False
    except KeyError:
        print("key error")
    return result


def randomStringwithDigitsAndSymbols(stringLength=10):
    """Generate a random string of letters, digits and special characters """

    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))


if __name__ == '__main__':
    app.secret_key = 'random string'
    app.debug = True
    # app.run()
    # app.run(host='192.168.2.146', port=811, threaded=True)
    http_server = WSGIServer(('0.0.0.0', 811), app)  # , keyfile='sslkeys/server.key', certfile='sslkeys/server.crt')
    http_server.serve_forever()

