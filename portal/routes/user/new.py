import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_restplus import Resource, reqparse, cors
from ...helpers import randomStringwithDigitsAndSymbols, token_verify
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/new")
class UserNew(Resource):
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @ns.doc(parser=parser,
        description='Create New User',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        try:
            if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
                auth = request.headers["Authorization"]
                auth1 = jwt.decode(auth, key=app.config['JWT_SECRET'])
                if auth1["role"] == "admin" and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
                    data = json.loads(str(request.data, encoding='utf-8'))
                    username = data["Username"]
                    displayname = data["DisplayName"]
                    email = data["Email"]
                    session_duration = data["SessionDuration"]
                    password = randomStringwithDigitsAndSymbols(10)
                    enc_pass = Encryption().encrypt(password)
                    userexist = Users.query.filter_by(Username=username).first()
                    if userexist is None:
                        new_user = Users(Username=username,
                                            Email=email,
                                            Password=enc_pass,
                                            Role=data["Role"],
                                            Status="active",
                                            TemporaryPassword=True,
                                            DisplayName=displayname,
                                            SessionDuration=session_duration,
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
