import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from ..helpers import randomStringwithDigitsAndSymbols, token_verify
from ..encryption import Encryption
from ..models import db
from ..models.users import Users
from ..models.security_question import SecurityQuestion


user_blueprint = Blueprint('user_blueprint', __name__, template_folder='templates')

@user_blueprint.route('/checkuserexists', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'User', 'Ipaddress'])
def check_user():
    if request.method == "POST":
        data = json.loads(str(request.data, encoding='utf-8'))
        username = data["username"]
        user_details = Users.query.filter_by(Username=username).first()
        if user_details is not None:
            return jsonify({
                "result": True
            }), 200
        else:
            return jsonify({"error": "user doesn't exist"}), 400
    else:
        return abort(404)

@user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
def create_user():
    if request.method == "POST":
        try:
            if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
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
                    enc_pass = Encryption().encrypt(password)
                    userexist = Users.query.filter_by(Username=username).first()
                    if userexist is None:
                        new_user = Users(Email=email,
                                            Password=enc_pass,
                                            Role=role,
                                            Status="active",
                                            TemporaryPassword=True,
                                            Username=username,
                                            DisplayName=displayname,
                                            SessionExpiry=session_expiry,
                                            UserCreatedTime=datetime.utcnow())
                        db.session.add(new_user)
                        db.session.commit()
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
            else:
                return jsonify({"error": "Not Authorized"}), 401
        except jwt.DecodeError:
            return jsonify({"error": "Not Authorized"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Not Authorized"}), 401
        except Exception as e:
            print(str(e))
            return jsonify({"error": "Not Authorized"}), 401




@user_blueprint.route('/securityquestion', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type'])
def get_security_question():
    if request.method == "POST":
        data = json.loads(str(request.data, encoding='utf-8'))
        username = data["username"]
        user_details = Users.query.filter_by(Username=username).first()
        if user_details is not None:
            sec_question = user_details["securityQuestion"]
            print(sec_question)
            question = SecurityQuestion.query.get(sec_question)
            return jsonify({"question": question.question, "email": user_details["email"]}), 200
        else:
            return jsonify({"error": "user doesn't exist"}), 400
    else:
        return "Not Found", 404


@user_blueprint.route('/setsecurityquestion', methods=['GET', 'POST', 'OPTIONS'])
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

                user = Users.query.get(data["username"])
                user.securityQuestionID = data["securityQuestion"]
                user.securityAnswer = Encryption().encrypt(data["answer"])
                db.session.commit()

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


@user_blueprint.route('/changepass', methods=['POST', 'OPTIONS'])
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
                    userinfo = Users.query.filter_by(Username=username).first()
                    if userinfo["Password"] == Encryption().encrypt(old_pass):
                        pass_encoded = Encryption().encrypt(new_pass)
                        userinfo.Password = pass_encoded
                        userinfo.TemporaryPassword = False
                        db.session.commit()
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


@user_blueprint.route('/login_cred', methods=['POST', 'OPTIONS'])
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
        pass_encypt = Encryption().encrypt(password)
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


@user_blueprint.route("/resetpass", methods=['POST', 'OPTIONS'])
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
            userdata = Users.query.filter_by(Username=id).first()
            if userdata["answer"] == Encryption().encrypt(answer):
                change_pass = True
        elif request_type == "email":
            userdata = Users.query.filter_by(Username=id).first()
            print(userdata)
            if userdata is not None and userdata["email"] == mail:
                change_pass = True

        if change_pass:
            try:
                password = randomStringwithDigitsAndSymbols()
                pass_encypt = Encryption().encrypt(password)
                msgtext = MIMEText('<p>Your password has been reset. The temporary password is: %s</p>'
                                   '<p>Please log into your system as soon as possible to set your new password.</p>'
                                   % password, 'html')
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")

                user = Users.query.get(id)
                user.password = pass_encypt
                user.TemporaryPassword = True
                db.session.commit()

                smtpObj.sendmail("venkateshvyyerram@gmail.com", mail, msg.as_string())
                return jsonify({"result": "Success"}), 200
            except Exception as e:
                print(str(e))
                return jsonify({"error": "sorry"}), 500

