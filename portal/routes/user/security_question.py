import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_restx import Resource, reqparse, cors, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, RESPONSE_OK

from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP

getParser = reqparse.RequestParser()
getParser.add_argument('Authorization', type=str, location='headers', required=True)
getParser.add_argument('username', type=str, location='headers', required=True)
getParser.add_argument('Ipaddress', type=str, location='headers', required=True)

postParser = reqparse.RequestParser()
postParser.add_argument('Authorization', type=str, location='headers', required=True)
postParser.add_argument('Ipaddress', type=str, location='headers', required=True)
postParser.add_argument('username', type=str, location='headers', required=True)

postParser.add_argument('SecurityQuestionID', type=int, location='json', required=True)
postParser.add_argument('SecurityAnswer', type=str, location='json', required=True)
postParser.add_argument('Email', type=str, location='json', required=True)
postParser.add_argument('PhoneNumber', type=str, location='json', required=False)

get_response_model = ns.model('GetSecurityQuestion', {
    'Question': fields.String,
    'Email': fields.String,
})

post_response_model = ns.model('PostSecurityQuestion', {
    'result': fields.String,
})

@ns.route("/security-question")
class SecurityQuestion(Resource):
    @ns.doc(parser=getParser,
            description='Get security question of a user',
            responses={
                200: 'OK',
                400: 'Bad Request',
                401: 'Unauthorized',
                404: 'Not Found',
                500: 'Internal Server Error'})
    @ns.expect(getParser)
    @ns.marshal_with(get_response_model)
    def get(self):
        args = getParser.parse_args(strict=True)

        user = Users.query.filter_by(Username=args['username']).first()
        if user is None:
            raise NotFound('User not found')

        question = user.SecurityQuestion.Question
        return {
                   "Question": question,
                   "Email": user.Email
               }, 200

    @ns.doc(parser=postParser,
            description='Set Security Question',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(postParser, validate=True)
    @ns.marshal_with(post_response_model)
    def post(self):
        args = postParser.parse_args(strict=False)
        token = args["Authorization"]
        if not token_verify(token=token, ip=args["Ipaddress"], user=args["username"]):
            raise Unauthorized()

        user = Users.query.filter_by(Username=args["username"]).first()
        if not user:
            raise NotFound()

        user.SecurityQuestionID = args["SecurityQuestionID"]
        user.SecurityAnswer = Encryption().encrypt(args["SecurityAnswer"])
        user.Email = args["Email"]
        try:
            db.session.commit()
            return RESPONSE_OK

        except KeyError as e:
            print(str(e))
            raise BadRequest
        except jwt.DecodeError:
            raise Unauthorized
        except jwt.ExpiredSignatureError:
            raise Unauthorized('Please refresh the token')
