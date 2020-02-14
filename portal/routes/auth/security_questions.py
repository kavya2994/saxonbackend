import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_restplus import Resource, reqparse, fields, cors
from werkzeug.exceptions import NotFound, BadRequest
from ...helpers import randomStringwithDigitsAndSymbols, token_verify
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion , SecurityQuestionModel
from . import ns
from ... import APP


parser = reqparse.RequestParser()

@ns.route("/security-questions")
class SecurityQuestions(Resource):
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'])
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
    @ns.marshal_with(ns.model('SecurityQuestions', SecurityQuestionModel))
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'])
    def get(self):
        args = parser.parse_args(strict=False)
        questions = SecurityQuestion.query.all()
        return questions

