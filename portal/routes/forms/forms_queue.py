import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models import db, status, roles
from ...models.contributionform import Contributionform
from ...models.enrollmentform import Enrollmentform
from ...models.terminationform import Terminationform
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION, TOKEN_FORMTYPE_ENROLLMENT
from ...models.comments import Comments
from ...models.status import *
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP

response_model_child = ns.model('GetFormQueueChild', {
    "Token": fields.String,
    "FormID": fields.String,
    "EmployerID": fields.String,
    "MemberName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "FileName": fields.String,
    "EmailID": fields.String
})

response_model = ns.model('GetFormQueue', {
    "forms_queue": fields.List(fields.Nested(response_model_child))
})

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('user', type=str, location='args', required=True)
parser.add_argument('role', type=str, location='args', required=True)


@ns.route("/myqueue")
class FormQueue(Resource):
    @ns.doc(description='Initiate Termination',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        if token["role"] not in [roles.ROLES_HR, roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        if args["role"] == roles.ROLES_REVIEW_MANAGER:
            if token["role"] != roles.ROLES_REVIEW_MANAGER:
                raise Unauthorized()
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom == token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.FormType == TOKEN_FORMTYPE_ENROLLMENT).all()

            for tokens_data, enrollments in enrollment_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": str(enrollments.FirstName if enrollments.FirstName is not None else "") + " " + str(enrollments.MiddleName if enrollments.MiddleName is not None else "") + " " + str(enrollments.LastName if enrollments.LastName is not None else ""),
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom == token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.FormType == TOKEN_FORMTYPE_TERMINATION).all()

            for tokens_data, terminations in termination_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": terminations.MemberName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })
            contribution_forms = Contributionform.query.filter(Contributionform.PendingFrom == ROLES_REVIEW_MANAGER,
                                                               Contributionform.Status == STATUS_PENDING)\
                .order_by(Contributionform.LastModifiedDate.desc()).all()
            for contributions in contribution_forms:
                forms_data.append({
                    "FormID": contributions.FormID,
                    "EmployerID": contributions.EmployerID,
                    "FormType": "Contribution",
                    "FormStatus": contributions.Status,
                    "LastModifiedDate": contributions.LastModifiedDate,
                    "FileName": str(contributions.FilePath).replace("/", "\\").split("\\")[
                        len(str(contributions.FilePath).replace("/", "\\").split("\\")) - 1] if contributions.FilePath is not None else ""
                })

            return {"forms_queue": forms_data}, 200
        elif args["role"] == roles.ROLES_EMPLOYER:
            employer_id = args["user"]
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom == token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id,
                Token.FormType == TOKEN_FORMTYPE_ENROLLMENT).all()

            for tokens_data, enrollments in enrollment_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": str(enrollments.FirstName if enrollments.FirstName is not None else "") + " " + str(enrollments.MiddleName if enrollments.MiddleName is not None else "") + " " + str(enrollments.LastName if enrollments.LastName is not None else ""),
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.FormStatus == status.STATUS_PENDING,
                Token.PendingFrom == token["role"],
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id,
                Token.FormType == TOKEN_FORMTYPE_TERMINATION).all()

            for tokens_data, terminations in termination_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": terminations.MemberName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate
                })

            return {"forms_queue": forms_data}, 200
