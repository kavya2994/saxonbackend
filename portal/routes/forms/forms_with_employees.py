import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, crossdomain, RESPONSE_OK
from ...models import db, status, roles
from ...models.enrollmentform import Enrollmentform
from ...models.terminationform import Terminationform, TerminationformResponseModel
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP
response_model = {
    "Token": fields.String,
    "EmployerID": fields.String,
    "MemberName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime
}

response = {
    "forms_employees": fields.List(fields.Nested(response_model))
}

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('offset', type=int, location='args', required=True)


@ns.route("/employees")
class FormWithEmployees(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Initiate Termination',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response)
    def get(self):
        args = parser.parse_args(strict=False)
        decode_token = token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        offset_ = args["offset"]
        if offset_ is None or str(offset_) == "":
            offset_ = 0
        offset_ = int(offset_)
        if decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom != roles.ROLES_REVIEW_MANAGER,
                Token.TokenStatus == status.STATUS_ACTIVE) \
                .offset(offset_) \
                .limit(25).all()

            for tokens_data, enrollments in enrollment_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": enrollments.MemberName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom != roles.ROLES_REVIEW_MANAGER,
                Token.TokenStatus == status.STATUS_ACTIVE)\
                .offset(offset_) \
                .limit(25).all()

            for tokens_data, terminations in termination_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": terminations.MemberName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })

            return {"forms_employees": forms_data}, 200
        elif decode_token["role"] in [roles.ROLES_EMPLOYER, roles.ROLES_HR]:
            employer_id = str(args["username"]).replace("HR", "")
            offset_ = args["offset"]
            if offset_ is None or str(offset_) == "":
                offset_ = 0
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom != decode_token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id)\
                .offset(offset_) \
                .limit(25).all()

            for tokens_data, enrollments in enrollment_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": enrollments.MemberName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom != decode_token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id)\
                .offset(offset_) \
                .limit(25).all()

            for tokens_data, terminations in termination_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": terminations.MemberName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })
            print(forms_data)
            return {"forms_employees": forms_data}, 200
