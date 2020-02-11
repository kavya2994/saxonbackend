import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns

parser = reqparse.RequestParser()

response_model = {
    'EmployerName': fields.String,
    'EmployerID': fields.String,
    'InitiatedDate': fields.DateTime,
    'AlreadyEnrolled': fields.String,
    'Status': fields.String,
    'FirstName': fields.String,
    'MiddleName': fields.String,
    'LastName': fields.String,
    'DOB': fields.String,
    'Title': fields.String,
    'MaritalStatus': fields.String,
    'MailingAddress': fields.String,
    'AddressLine2': fields.String,
    'District': fields.String,
    'PostalCode': fields.String,
    'Country': fields.String,
    'EmailAddress': fields.String,
    'Telephone': fields.String,
    'StartDateofContribution': fields.DateTime,
    'StartDateofEmployment': fields.DateTime,
    'ConfirmationStatus': fields.String,
    'SignersName': fields.String,
    'Signature': fields.String,
    'Estimatedannualincomerange': fields.String,
    'ImmigrationStatus': fields.String,
    'PendingFrom': fields.String,
    'SpouseName': fields.String,
    'SpouseDOB': fields.String,
    'FilePath': fields.String,
}


@ns.route("/<TokenID>")
class GetEnrollmentFormData(Resource):
    @ns.doc(parser=parser,
        description='Get Enrollment Data',
        responses={
            200: 'OK',
            400: 'BadRequest',
            500: 'Internal Server Error'
        })

    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self, TokenID):
        args = parser.parse_args()
        try:
            token = Token.query.get(TokenID)
            if token is None:
                raise BadRequest()

            enrollmentform = Enrollmentform.query.get(token.FormID)

            return enrollmentform
        except Exception as e:
            print(e)
            raise InternalServerError()
