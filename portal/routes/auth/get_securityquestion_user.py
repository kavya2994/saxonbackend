import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_restplus import Resource, reqparse, fields, cors
from werkzeug.exceptions import NotFound, BadRequest
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, crossdomain
from ...encryption import Encryption
from werkzeug.exceptions import NotFound, BadRequest, UnprocessableEntity, InternalServerError
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion, SecurityQuestionModel
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, location='args', required=True)

response_model = {
    "question": fields.String
}


@ns.route("/user/securityquestion")
class SecurityQuestionsForUser(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @ns.doc(parser=parser,
            description='Get list of security questions',
            responses={
                200: 'OK',
                400: 'Bad Request',
                401: 'Unauthorized',
                404: 'Not Found',
                500: 'Internal Server Error'})
    @ns.expect(parser)
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args()
        username = args["username"]
        users, question = db.session.query(Users, SecurityQuestion).filter(Users.Username == username,
                                                         Users.SecurityQuestionID == SecurityQuestion.SecurityQuestionID).first()

        if question is None:
            raise UnprocessableEntity("Question realted to user not found")

        return {"question": question.Question}, 200
