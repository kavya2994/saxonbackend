import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models import db, status, roles
from ...models.enrollmentform import Enrollmentform
from ...models.terminationform import Terminationform
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP


response_model_child = ns.model('GetFormWithEmployeesChild', {
    "Token": fields.String,
    "EmployerID": fields.String,
    "MemberName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "EmailID": fields.String,
    "PendingFrom": fields.String
})

response_model = ns.model('GetFormWithEmployees', {
    "forms_employees": fields.List(fields.Nested(response_model_child))
})

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('offset', type=int, location='args', required=True)
parser.add_argument('user', type=str, location='args', required=True)


@ns.route("/employees")
class FormWithEmployees(Resource):
    @ns.doc(description='Initiate Termination',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
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
                    "MemberName": enrollments.FirstName if enrollments.FirstName is not None else "" + " " + enrollments.MiddleName if enrollments.MiddleName is not None else "" + " " + enrollments.LastName if enrollments.LastName is not None else "",
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "PendingFrom": tokens_data.PendingFrom,
                    "EmailID": enrollments.EmailAddress
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
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "PendingFrom": tokens_data.PendingFrom,
                    "EmailID": terminations.EmailAddress
                })

            return {"forms_employees": forms_data}, 200
        elif decode_token["role"] in [roles.ROLES_EMPLOYER, roles.ROLES_HR]:
            employer_id = args["user"]
            offset_ = args["offset"]
            if offset_ is None or str(offset_) == "":
                offset_ = 0
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom == roles.ROLES_MEMBER,
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id)\
                .offset(offset_) \
                .limit(25).all()

            for tokens_data, enrollments in enrollment_form_data:

                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": enrollments.FirstName if enrollments.FirstName is not None else "" + " " + enrollments.MiddleName if enrollments.MiddleName is not None else "" + " " + enrollments.LastName if enrollments.LastName is not None else "",
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "PendingFrom": tokens_data.PendingFrom,
                    "EmailID": enrollments.EmailAddress
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom == roles.ROLES_MEMBER,
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
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "PendingFrom": tokens_data.PendingFrom,
                    "EmailID": terminations.EmailAddress
                })
            print(forms_data)
            return {"forms_employees": forms_data}, 200
