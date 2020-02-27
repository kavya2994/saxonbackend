import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request, abort
from flask_restx import Resource, reqparse, fields, cors
from werkzeug.exceptions import NotFound, BadRequest
from ...helpers import randomStringwithDigitsAndSymbols, token_verify
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP

parser = reqparse.RequestParser()


SecurityQuestionModel = ns.model('GetSecurityQuestiondQuestion', {
    'SecurityQuestionID': fields.Integer,
    'Question': fields.String,
})

response_model = ns.model('GetSecurityQuestions', {
    "questions": fields.List(fields.Nested(SecurityQuestionModel))
})


@ns.route("/security-questions")
class SecurityQuestions(Resource):
    @ns.doc(description='Get list of security questions',
            responses={
                200: 'OK',
                400: 'Bad Request',
                401: 'Unauthorized',
                404: 'Not Found',
                500: 'Internal Server Error'})
    @ns.expect(parser)
    @ns.marshal_with(response_model)
    def get(self):
        questions = SecurityQuestion.query.all()
        question_list = []
        for question in questions:
            question_list.append({
                'SecurityQuestionID': question.SecurityQuestionID,
                'Question': question.Question
            })
        return {"questions": question_list}, 200
