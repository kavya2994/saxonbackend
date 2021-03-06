import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models import db, status, roles
from ...models.enrollmentform import Enrollmentform
from ...models.terminationform import Terminationform
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION, TOKEN_FORMTYPE_ENROLLMENT
from ...models.contributionform import Contributionform
from ...models.documents import Documents
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
parser.add_argument('user', type=str, location='args', required=True)
parser.add_argument('role', type=str, location='args', required=True)

response_model_child = ns.model('GetMyFormsChild', {
    "Token": fields.String,
    "FormID": fields.String,
    "EmployerID": fields.String,
    "EmployerName": fields.String,
    "MemberName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "FileName": fields.String,
    "EmailID": fields.String,
    "PendingFrom": fields.String
})

response_model = ns.model('GetMyForms', {
    "myforms": fields.List(fields.Nested(response_model_child))
})


@ns.route("/my")
class MyForms(Resource):
    @ns.doc(description='Get my forms',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        offset = args["offset"]
        if offset is None or str(offset) == "":
            offset = 0
        offset = int(offset)
        if token["role"] not in [roles.ROLES_HR, roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        if args["role"] == roles.ROLES_REVIEW_MANAGER:
            if token["role"] != roles.ROLES_REVIEW_MANAGER:
                raise Unauthorized()
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.FormType == TOKEN_FORMTYPE_ENROLLMENT).order_by(Token.LastModifiedDate.desc()) \
                .offset(offset) \
                .limit(25).all()

            for tokens_data, enrollments in enrollment_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": str(enrollments.FirstName if enrollments.FirstName is not None else "") + " " + str(enrollments.LastName if enrollments.LastName is not None else ""),
                    "FormType": tokens_data.FormType,
                    "EmployerName": enrollments.EmployerName,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "EmailID": enrollments.EmailAddress,
                    "PendingFrom": tokens_data.PendingFrom
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.FormType == TOKEN_FORMTYPE_TERMINATION).order_by(Token.LastModifiedDate.desc()) \
                .offset(offset) \
                .limit(25).all()

            for tokens_data, terminations in termination_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": terminations.MemberName,
                    "EmployerName": terminations.EmployerName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "EmailID": terminations.EmailAddress,
                    "PendingFrom": tokens_data.PendingFrom
                })

            contribution_forms = Contributionform.query.filter(Contributionform.Status != status.STATUS_DELETE)\
                .order_by(Contributionform.LastModifiedDate.desc()).all()
            for contributions in contribution_forms:
                forms_data.append({
                    "FormID": contributions.FormID,
                    "EmployerID": contributions.EmployerID,
                    "EmployerName": contributions.EmployerName,
                    "FormType": "Contribution",
                    "FormStatus": contributions.Status,
                    "LastModifiedDate": contributions.LastModifiedDate,
                    "PendingFrom": contributions.PendingFrom,
                    "FileName": str(contributions.FilePath).replace("/", "\\").split("\\")[len(str(contributions.FilePath).replace("/", "\\").split("\\")) - 1] if contributions.FilePath is not None else ""
                })
            # documents = Documents.query.order_by(Documents.Date.desc()).all()
            # for document in documents:
            #     forms_data.append({
            #         "FormID": document.FormID,
            #         "EmployerID": document.EmployerID,
            #         "EmployerName": document.EmployerName,
            #         "FormType": "Document",
            #         "FormStatus": document.Status,
            #         "LastModifiedDate": document.LastModifiedDate,
            #         "PendingFrom": document.PendingFrom,
            #         "FileName": str(document.FilePath).replace("/", "\\").split("\\")[len(
            #             str(document.FilePath).replace("/", "\\").split(
            #                 "\\")) - 1] if document.FilePath is not None else ""
            #     })
            #     print("form_data", forms_data)
            return {"myforms": forms_data}, 200
        elif args["role"] == roles.ROLES_EMPLOYER:
            employer_id = args["user"]
            offset = args["offset"]
            if offset is None or str(offset) == "":
                offset = 0
            forms_data = []
            enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                Token.FormID == Enrollmentform.FormID,
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id,
                Token.FormType == TOKEN_FORMTYPE_ENROLLMENT).order_by(Token.LastModifiedDate.desc()) \
                .offset(offset) \
                .limit(25).all()

            for tokens_data, enrollments in enrollment_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": str(enrollments.FirstName if enrollments.FirstName is not None else "") + " " + str(enrollments.LastName if enrollments.LastName is not None else ""),
                    "FormType": tokens_data.FormType,
                    "EmployerName": enrollments.EmployerName,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "EmailID": enrollments.EmailAddress,
                    "PendingFrom": tokens_data.PendingFrom
                })

            termination_form_data = db.session.query(Token, Terminationform).filter(
                Token.FormID == Terminationform.FormID,
                Token.TokenStatus == status.STATUS_ACTIVE,
                Token.EmployerID == employer_id,
                Token.FormType == TOKEN_FORMTYPE_TERMINATION).order_by(Token.LastModifiedDate.desc()) \
                .offset(offset) \
                .limit(25).all()

            for tokens_data, terminations in termination_form_data:
                forms_data.append({
                    "Token": tokens_data.TokenID,
                    "EmployerID": tokens_data.EmployerID,
                    "MemberName": terminations.MemberName,
                    "EmployerName": terminations.EmployerName,
                    "FormType": tokens_data.FormType,
                    "FormStatus": tokens_data.FormStatus,
                    "LastModifiedDate": tokens_data.LastModifiedDate,
                    "EmailID": terminations.EmailAddress,
                    "PendingFrom": tokens_data.PendingFrom
                })
            # contribution_forms = Contributionform.query.order_by(Contributionform.LastModifiedDate.desc()).all()
            # for contributions in contribution_forms:
            #     forms_data.append({
            #         "FormID": contributions.FormID,
            #         "EmployerID": contributions.EmployerID,
            #         "FormType": "Contribution",
            #         "FormStatus": contributions.Status,
            #         "LastModifiedDate": contributions.LastModifiedDate,
            #         "FilePath": contributions.FilePath
            #     })

            return {"myforms": forms_data}, 200
