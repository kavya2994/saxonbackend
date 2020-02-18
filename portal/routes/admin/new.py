import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, crossdomain, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.users import Users
from ...services.mail import send_email
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/createuser")
class AddUser(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Create New User',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if token["role"] == roles.ROLES_ADMIN:
            data = json.loads(str(request.data, encoding='utf-8'))
            print(data)
            username = data["username"]
            displayname = data["displayname"]
            email = data["email"]
            # session_duration = data["SessionDuration"]
            password = randomStringwithDigitsAndSymbols(10)
            enc_pass = Encryption().encrypt(password)
            userexist = Users.query.filter_by(Username=username).first()
            if userexist is None:
                new_user = Users(Username=username,
                                 UserID=1000,
                                 Email=email,
                                 Password=enc_pass,
                                 Role=data["role"],
                                 Status=status.STATUS_ACTIVE,
                                 TemporaryPassword=True,
                                 DisplayName=displayname,
                                 SessionDuration="30",
                                 UserCreatedTime=datetime.utcnow())
                db.session.add(new_user)
                db.session.commit()
                msg_text = MIMEText('<p>Dear %s</p>'
                                    '<p>Your account is created please use this password %s to log in</p>'
                                    % (displayname, password))

                send_email(email, "Welcome to Pension Management portal", body=msg_text)
                return {"result": "Success"}, 200
            elif userexist.Status == status.STATUS_DELETE:
                userexist.UserID = 1000
                userexist.Username = username,
                userexist.Email = email,
                userexist.Password = enc_pass,
                userexist.Role = data["role"],
                userexist.Status = status.STATUS_ACTIVE,
                userexist.TemporaryPassword = True,
                userexist.DisplayName = displayname,
                userexist.SessionDuration = "30",
                userexist.UserCreatedTime = datetime.utcnow()
                return {"result": "Success"}, 200
            else:
                return {"error": "Username already exists"}, 409
        else:
            return {"error": "Not Authorized"}, 401

