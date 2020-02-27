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
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('FormType', type=str, location='json', required=True)
parser.add_argument('Employer', type=str, location='json', required=False)
parser.add_argument('Member', type=str, location='json', required=False)
parser.add_argument('SubmittedFrom', type=str, location='json', required=True)
parser.add_argument('SubmittedTo', type=str, location='json', required=True)
# parser.add_argument('offset', type=int, location='args', required=True)

response_model_child = ns.model('PostSearchFormsChild', {
    "Token": fields.String,
    "FormID": fields.String,
    "EmployerID": fields.String,
    "MemberName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "FilePath": fields.String
})

response_model = ns.model('PostSearchForms', {
    "forms": fields.List(fields.Nested(response_model_child))
})


@ns.route("/search")
class SearchForms(Resource):
    @ns.doc(description='Get my forms',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        forms_data = []
        parameters = ["FormType", "Status", "Employer", "Member", "SubmittedFrom", "SubmittedTo"]
        parameters_dict = {}
        for arg in parameters:
            if args[arg] is None:
                parameters_dict[arg] = ""
            else:
                parameters_dict[arg] = args[arg]
        try:
            form_status = args["FormStatus"]
            submitted_from = args["SubmittedFrom"]
            submitted_to = args["SubmittedTo"]
            if args["FormType"] == TOKEN_FORMTYPE_TERMINATION:

                termination_form_data = db.session.query(Token, Terminationform).filter(
                    Token.FormType == TOKEN_FORMTYPE_TERMINATION,
                    Token.TokenStatus == status.STATUS_ACTIVE,
                    Terminationform.EmployerName.like("%" + parameters_dict["Employer"] + "%"),
                    Terminationform.MemberName.like("%" + parameters_dict["Member"] + "%")).order_by(
                    Token.LastModifiedDate.desc()).all()
                # still date criteria pending
                for tokens_data, terminations in termination_form_data:
                    forms_data.append({
                        "Token": tokens_data.TokenID,
                        "EmployerID": tokens_data.EmployerID,
                        "MemberName": terminations.MemberName,
                        "FormType": tokens_data.FormType,
                        "FormStatus": tokens_data.FormStatus,
                        "LastModifiedDate": tokens_data.LastModifiedDate
                    })
                return {"forms": forms_data}, 200
            elif args["FormType"] == TOKEN_FORMTYPE_ENROLLMENT:
                enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
                    Token.FormStatus == status.STATUS_PENDING,
                    Token.TokenStatus == status.STATUS_ACTIVE).order_by(Token.LastModifiedDate.desc()).all()

                for tokens_data, enrollments in enrollment_form_data:
                    forms_data.append({
                        "Token": tokens_data.TokenID,
                        "EmployerID": tokens_data.EmployerID,
                        "MemberName": enrollments.MemberName,
                        "FormType": tokens_data.FormType,
                        "FormStatus": tokens_data.FormStatus,
                        "LastModifiedDate": tokens_data.LastModifiedDate
                    })
        except Exception as e:
            LOG.error("Exception while adding employer to member", e)
            raise InternalServerError("Can't add employer to user")
