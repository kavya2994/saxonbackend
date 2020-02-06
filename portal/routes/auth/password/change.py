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

@ns.route("/password/change")
class PasswordChange(Resource):
    @ns.doc(parser=parser,
        description='Change Password',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        try:
            print(request.headers)
            print(request.data)
            data = json.loads(str(request.data, encoding='utf-8'))
            # token = request.headers["Authorization"]
            if 'Authorization' in request.headers.keys() and token_verify(request.headers["Authorization"],
                                                                          request.headers["User"],
                                                                          request.headers["Ipaddress"]):

                username = data["Username"]
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

