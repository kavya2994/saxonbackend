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
from ...models.contributionform import Contributionform
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('offset', type=int, location='args', required=True)

response_model = {
    "Token": fields.String,
    "FormID": fields.String,
    "EmployerID": fields.String,
    "MemberName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "FilePath": fields.String
}

response = {
    "myforms": fields.List(fields.Nested(response_model))
}


@ns.route("/my")
class MyForms(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get my forms',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def get(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        offset = args["offset"]
        if offset is None or str(offset) == "":
            offset = 0
        offset = int(offset)
        if token["role"] == roles.ROLES_REVIEW_MANAGER:
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom != roles.ROLES_REVIEW_MANAGER,
                Token.TokenStatus == status.STATUS_ACTIVE) \
                .offset(offset) \
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
                Token.TokenStatus == status.STATUS_ACTIVE) \
                .offset(offset) \
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

            contribution_forms = Contributionform.query.order_by(Contributionform.LastModifiedDate.desc()).all()
            for contributions in contribution_forms:
                forms_data.append({
                    "FormID": contributions.FormID,
                    "EmployerID": contributions.EmployerID,
                    "FormType": "Contribution",
                    "FormStatus": contributions.Status,
                    "LastModifiedDate": contributions.LastModifiedDate,
                    "FilePath": contributions.FilePath
                })

            return {"myforms": forms_data}, 200
        elif token["role"] in [roles.ROLES_EMPLOYER, roles.ROLES_HR]:
            employer_id = str(args["username"]).replace("HR", "")
            offset = args["offset"]
            if offset is None or str(offset) == "":
                offset = 0
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom != token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id) \
                .offset(offset) \
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
                Token.PendingFrom != token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id) \
                .offset(offset) \
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
            contribution_forms = Contributionform.query.order_by(Contributionform.LastModifiedDate.desc()).all()
            for contributions in contribution_forms:
                forms_data.append({
                    "FormID": contributions.FormID,
                    "EmployerID": contributions.EmployerID,
                    "FormType": "Contribution",
                    "FormStatus": contributions.Status,
                    "LastModifiedDate": contributions.LastModifiedDate,
                    "FilePath": contributions.FilePath
                })

            return {"myforms": forms_data}, 200
