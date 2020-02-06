import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from ....helpers import randomStringwithDigitsAndSymbols, token_verify
from ....encryption import Encryption
from ....models import db
from ....models.users import Users
from ....models.security_question import SecurityQuestion
from .. import ns


parser = reqparse.RequestParser()
parser.add_argument('Username', type=str, location='json', required=True)
parser.add_argument('Password', type=str, location='json', required=True)
parser.add_argument('IP', type=str, location='json', required=False)

@ns.route("/password/reset")
class PasswordReset(Resource):
    @ns.doc(parser=parser,
        description='Reset Password',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        print(request.data)
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        change_pass = False
        request_type = data["request_type"]
        id = data["Username"]
        mail = data["Email"]
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
            answer = data["Answer"]
            userdata = Users.query.filter_by(Username=id).first()
            if userdata["Answer"] == Encryption().encrypt(answer):
                change_pass = True
        elif request_type == "email":
            userdata = Users.query.filter_by(Username=id).first()
            print(userdata)
            if userdata is not None and userdata["Email"] == mail:
                change_pass = True

        if change_pass:
            try:
                password = randomStringwithDigitsAndSymbols()
                pass_encrypt = Encryption().encrypt(password)
                msgtext = MIMEText('<p>Your password has been reset. The temporary password is: %s</p>'
                                   '<p>Please log into your system as soon as possible to set your new password.</p>'
                                   % password, 'html')
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")

                user = Users.query.get(id)
                user.Password = pass_encrypt
                user.TemporaryPassword = True
                db.session.commit()

                smtpObj.sendmail("venkateshvyyerram@gmail.com", mail, msg.as_string())
                return jsonify({"result": "Success"}), 200
            except Exception as e:
                print(str(e))
                return jsonify({"error": "sorry"}), 500
