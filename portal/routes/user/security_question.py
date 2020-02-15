import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_restplus import Resource, reqparse, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, crossdomain, RESPONSE_OK
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP


getParser = reqparse.RequestParser()
getParser.add_argument('Authorization', type=str, location='headers', required=True)
getParser.add_argument('Username', type=str, location='headers', required=True)
getParser.add_argument('IpAddress', type=str, location='headers', required=True)

postParser = reqparse.RequestParser()
postParser.add_argument('Authorization', type=str, location='headers', required=True)
postParser.add_argument('IpAddress', type=str, location='headers', required=True)
postParser.add_argument('Username', type=str, location='headers', required=True)

postParser.add_argument('SecurityQuestionID', type=int, location='json', required=True)
postParser.add_argument('SecurityAnswer', type=str, location='json', required=True)

@ns.route("/security-question")
class SecurityQuestion(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=getParser,
        description='Get security question of a user',
        responses={
            200: 'OK',
            400: 'Bad Request',
            401: 'Unauthorized',
            404: 'Not Found',
            500: 'Internal Server Error'})
    @ns.expect(getParser)
    def get(self):
        args = getParser.parse_args(strict=True)

        user = Users.query.filter_by(Username=args['Username']).first()
        if user is None:
            raise NotFound('User not found')

        question = user.SecurityQuestion.Question
        return {
            "Question": question,
            "Email": user.Email
        }, 200



    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=postParser,
        description='Set Security Question',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(postParser, validate=True)
    def post(self):
        args = postParser.parse_args(strict=False)
        token = args["Authorization"]
        if not token_verify(token=token, ip=args["IpAddress"], user=args["Username"]):
            raise Unauthorized()

        user = Users.query.filter_by(Username=args["Username"]).first()
        if not user:
            raise NotFound()

        user.SecurityQuestionID = args["SecurityQuestionID"]
        user.SecurityAnswer = Encryption().encrypt(args["SecurityAnswer"])
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
