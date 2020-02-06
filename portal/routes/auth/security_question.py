import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from ...helpers import randomStringwithDigitsAndSymbols, token_verify
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Username', type=str, location='json', required=False)
parser.add_argument('Password', type=str, location='json', required=False)
parser.add_argument('IP', type=str, location='json', required=False)

@ns.route("/security-question")
class ResetPassword(Resource):
    @ns.doc(parser=parser,
        description='Get Security Question',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
        data = json.loads(str(request.data, encoding='utf-8'))
        username = data["Username"]
        user_details = Users.query.filter_by(Username=username).first()
        if user_details is not None:
            sec_question_id = user_details["SecurityQuestionID"]
            print(sec_question)
            question = SecurityQuestion.query.get(sec_question_id)
            return jsonify({"question": question.Question, "email": user_details["Email"]}), 200
        else:
            return jsonify({"error": "user doesn't exist"}), 400



    @ns.doc(parser=None,
        description='Set Security Question',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"], user=request.headers["User"]):
            try:
                auth = request.headers["Authorization"]
                auth = jwt.decode(auth, key='secret')
                data = json.loads(str(request.data, encoding='utf-8'))

                user = Users.query.get(data["Username"])
                user.SecurityQuestionID = data["SecurityQuestionID"]
                user.SecurityAnswer = Encryption().encrypt(data["SecurityAnswer"])
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
