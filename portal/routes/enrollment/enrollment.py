
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
getParser.add_argument('Authorization', type=str, location='headers', required=True)
getParser.add_argument('Username', type=str, location='headers', required=True)
getParser.add_argument('IpAddress', type=str, location='headers', required=True)


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

parser.add_argument('RequestType', type=str, location='json', required=True, help='Valid Values: [SaveFormData]')
parser.add_argument('EmployerName', type=str, location='json', required=True)
parser.add_argument('EmployerID', type=str, location='json', required=True)
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
parser.add_argument('SignersName', type=str, location='json', required=True)
parser.add_argument('Signature', type=str, location='json', required=True)
parser.add_argument('Estimatedannualincomerange', type=str, location='json', required=True)
parser.add_argument('ImmigrationStatus', type=str, location='json', required=True)
parser.add_argument('PendingFrom', type=str, location='json', required=True)
parser.add_argument('SpouseName', type=str, location='json', required=True)
parser.add_argument('SpouseDOB', type=inputs.date_from_iso8601, location='json', required=True)


@ns.route("/<FormID>")
class Token(Resource):
    @ns.doc(parser=getParser,
        description='Get Enrollment Data by FormID',
        responses={
            200: 'OK',
            401: 'Unauthorized',
            404: 'NotFound',
            500: 'Internal Server Error'
        })

    @ns.expect(getParser, validate=True)
    @ns.marshal_with(EnrollmentformResponseModel)
    def get(self, FormID):
        args = getParser.parse_args()
        auth = token_verify_or_raise(token=args["Authorization"], ip=args["IpAddress"], user=args["Username"])

        enrollmentform = Enrollmentform.query.get(FormID)

        if enrollmentform is None:
            raise NotFound

        return enrollmentform


    @ns.doc(parser=parser,
        description='Update Enrollment Data by FormID',
        responses={
            200: 'OK',
            400: 'BadRequest',
            500: 'Internal Server Error'
        })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(EnrollmentformResponseModel)
    def post(self, FormID):
        args = parser.parse_args(strict=True)
        if args['RequestType'] != 'SaveFormData':
            raise BadRequest()

        form = Enrollmentform.query.get(FormID)
        if form is None:
            raise NotFound()

        try:
            form.EmployerName = args['EmployerName']
            form.EmployerID = args['EmployerID']
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
            form.SignersName = args['SignersName']
            form.Signature = args['Signature']
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
