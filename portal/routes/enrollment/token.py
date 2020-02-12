import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields, inputs
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify, token_verify_or_raise
from ...models.enrollmentform import Enrollmentform, EnrollmentformResponseModel
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns

getParser = reqparse.RequestParser()
parser = reqparse.RequestParser()

parser.add_argument('RequestType', type=str, location='json', required=True, help='Valid Values: [MemberSubmission]')
parser.add_argument('FirstName', type=str, location='json', required=True)
parser.add_argument('MiddleName', type=str, location='json', required=True)
parser.add_argument('LastName', type=str, location='json', required=True)
parser.add_argument('DOB', type=inputs.date_from_iso8601, location='json', required=True)
parser.add_argument('Title', type=str, location='json', required=True)
parser.add_argument('MaritalStatus', type=str, location='json', required=True)
parser.add_argument('MailingAddress', type=str, location='json', required=True)
parser.add_argument('AddressLine2', type=str, location='json', required=True)
parser.add_argument('District', type=str, location='json', required=True)
parser.add_argument('PostalCode', type=str, location='json', required=True)
parser.add_argument('Country', type=str, location='json', required=True)
parser.add_argument('EmailAddress', type=str, location='json', required=True)
parser.add_argument('Telephone', type=str, location='json', required=True)
parser.add_argument('StartDateofContribution', type=inputs.date_from_iso8601, location='json', required=True, help='iso8601 format. eg: 2012-11-25')
parser.add_argument('StartDateofEmployment', type=inputs.date_from_iso8601, location='json', required=True, help='iso8601 format. eg: 2012-11-25')
parser.add_argument('ConfirmationStatus', type=str, location='json', required=True)
parser.add_argument('Estimatedannualincomerange', type=str, location='json', required=True)
parser.add_argument('ImmigrationStatus', type=str, location='json', required=True)
parser.add_argument('PendingFrom', type=str, location='json', required=True)
parser.add_argument('SpouseName', type=str, location='json', required=True)
parser.add_argument('SpouseDOB', type=inputs.date_from_iso8601, location='json', required=True)


@ns.route("/token/<TokenID>")
class EnrollmentFormData(Resource):
    @ns.doc(parser=getParser,
        description='Get Enrollment Data by TokenID',
        responses={
            200: 'OK',
            400: 'BadRequest',
            500: 'Internal Server Error'
        })

    @ns.expect(getParser, validate=True)
    @ns.marshal_with(EnrollmentformResponseModel)
    def get(self, TokenID):
        args = getParser.parse_args()
        token = Token.query.get(TokenID)

        if token is None:
            raise BadRequest()

        try:
            enrollmentform = Enrollmentform.query.get(token.FormID)
            return enrollmentform
        except Exception as e:
            print(e)
            raise InternalServerError()


    @ns.doc(parser=parser,
        description='Update Enrollment Data by TokenID',
        responses={
            200: 'OK',
            400: 'BadRequest',
            404: 'NotFound',
            500: 'Internal Server Error'
        })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(EnrollmentformResponseModel)
    def post(self, TokenID):
        args = parser.parse_args(strict=True)
        if args['RequestType'] != 'MemberSubmission':
            raise BadRequest()

        token = Token.query.get(TokenID)
        if token is None:
            raise NotFound()

        try:
            form = Enrollmentform.query.get(token.FormID)
            form.FirstName = args['FirstName']
            form.MiddleName = args['MiddleName']
            form.LastName = args['LastName']
            form.DOB = args['DOB']
            form.Title = args['Title']
            form.MaritalStatus = args['MaritalStatus']
            form.MailingAddress = args['MailingAddress']
            form.AddressLine2 = args['AddressLine2']
            form.District = args['District']
            form.PostalCode = args['PostalCode']
            form.Country = args['Country']
            form.EmailAddress = args['EmailAddress']
            form.Telephone = args['Telephone']
            form.StartDateofContribution = args['StartDateofContribution']
            form.StartDateofEmployment = args['StartDateofEmployment']
            form.ConfirmationStatus = args['ConfirmationStatus']
            form.Estimatedannualincomerange = args['Estimatedannualincomerange']
            form.ImmigrationStatus = args['ImmigrationStatus']
            form.PendingFrom = args['PendingFrom']
            form.SpouseName = args['SpouseName']
            form.SpouseDOB = args['SpouseDOB']
            db.session.commit()

            return form
        except Exception as e:
            print(e)
            raise InternalServerError()
