import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_restplus import Resource, reqparse
from ...helpers import randomStringwithDigitsAndSymbols, token_verify
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns



parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('ipAddress', type=str, location='headers', required=True)


# @user_blueprint.route('/checkuserexists', methods=['GET', 'POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'User', 'Ipaddress'])
def check_user():
    if request.method == "POST":
        data = json.loads(str(request.data, encoding='utf-8'))
        user_details = Users.query.filter_by(Username=data["username"]).first()
        if user_details is not None:
            return jsonify({
                "result": True
            }), 200
        else:
            return jsonify({"error": "user doesn't exist"}), 400
    else:
        return abort(404)



# @user_blueprint.route('/login_cred', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type'])
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

