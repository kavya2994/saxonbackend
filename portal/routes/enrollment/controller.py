import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, fields, inputs, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models.comments import Comments
from ...models.roles import *
from ...models import db
from ...api import api
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

RequestType_MemberSubmission = 'MemberSubmission'
RequestType_SaveFormData = 'SaveFormData'
RequestType_EmployerSubmission = 'EmployerSubmission'
RequestType_ApprovalConfirmation = 'ApprovalConfirmation'
RequestType_Reject = 'Rejected'

getParser = reqparse.RequestParser()
parser = reqparse.RequestParser()

parser.add_argument('Authorization', type=str, location='headers', required=False)
parser.add_argument('username', type=str, location='headers', required=False)
parser.add_argument('Ipaddress', type=str, location='headers', required=False)

parser.add_argument('RequestType', type=str, location='json', required=True,
                    help=f"Valid Values: [{RequestType_MemberSubmission}, {RequestType_SaveFormData}, {RequestType_EmployerSubmission}, {RequestType_ApprovalConfirmation}, {RequestType_Reject}]")
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
parser.add_argument('StartDateofContribution', type=inputs.date_from_iso8601, location='json', required=True,
                    help='iso8601 format. eg: 2012-11-25')
parser.add_argument('StartDateofEmployment', type=inputs.date_from_iso8601, location='json', required=True,
                    help='iso8601 format. eg: 2012-11-25')
parser.add_argument('ConfirmationStatus', type=str, location='json', required=True)
parser.add_argument('EstimatedAnnualIncomeRange', type=str, location='json', required=True)
parser.add_argument('ImmigrationStatus', type=str, location='json', required=True)
parser.add_argument('SpouseName', type=str, location='json', required=True)
parser.add_argument('SpouseDOB', type=inputs.date_from_iso8601, location='json', required=True)
parser.add_argument('EmployerName', type=str, location='json', required=False)
parser.add_argument('EmployerID', type=str, location='json', required=False)
parser.add_argument('SignersName', type=str, location='json', required=False)
parser.add_argument('Signature', type=str, location='json', required=False)
parser.add_argument('RejectionReason', type=str, location='json', required=False)



response_model = ns.model('GetEnrollmentController', {
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
    'EstimatedAnnualIncomeRange': fields.String,
    'ImmigrationStatus': fields.String,
    'PendingFrom': fields.String,
    'SpouseName': fields.String,
    'SpouseDOB': fields.String,
    'FilePath': fields.String,
})

@ns.route("/token/<TokenID>")
class EnrollmentController(Resource):
    @ns.doc(description='Get Enrollment Data by TokenID',
            responses={
                200: 'OK',
                400: 'BadRequest',
                500: 'Internal Server Error'
            })
    @ns.expect(getParser, validate=True)
    @ns.marshal_with(response_model)
    def get(self, TokenID):
        args = getParser.parse_args()
        token = Token.query.get(TokenID)

        if token is None:
            raise BadRequest()

        try:
            enrollmentform = Enrollmentform.query.get(token.FormID)
            return enrollmentform
        except Exception as e:
            LOG.warning('Unexpected error happened during handling enrollment: %s', e)
            raise InternalServerError()

    @ns.doc(description='Update Enrollment Data by TokenID',
            responses={
                200: 'OK',
                400: 'BadRequest',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self, TokenID):
        args = parser.parse_args(strict=True)

        token = Token.query.get(TokenID)
        if token is None:
            raise NotFound('Token Not Found')

        form = Enrollmentform.query.get(token.FormID).first()
        if form is None:
            raise NotFound('Form Not Found')

        if args['RequestType'] == RequestType_MemberSubmission:
            self._memberSubmission_pre_update(token, form, args)
        elif args['RequestType'] == RequestType_SaveFormData:
            self._saveFormData_pre_update(token, form, args)
        elif args['RequestType'] == RequestType_EmployerSubmission:
            self._employerSubmission_pre_update(token, form, args)
        elif args['RequestType'] == RequestType_ApprovalConfirmation:
            self._approvalConfirmation_pre_update(token, form, args)
        elif args['RequestType'] == RequestType_Reject:
            self._reject_pre_update(token, form, args)
        else:
            raise BadRequest('Unkown RequestType')

        try:
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
            form.EstimatedAnnualIncomeRange = args['EstimatedAnnualIncomeRange']
            form.ImmigrationStatus = args['ImmigrationStatus']
            form.SpouseName = args['SpouseName']
            form.SpouseDOB = args['SpouseDOB']

            if args['RequestType'] != 'MemberSubmission':
                if 'EmployerName' in args:
                    form.EmployerName = args['EmployerName']

                if 'EmployerID' in args:
                    form.EmployerID = args['EmployerID']

                if 'SignersName' in args:
                    form.SignersName = args['SignersName']

                if 'Signature' in args:
                    form.Signature = args['Signature']

            db.session.commit()
        except Exception as e:
            LOG.warning('Unexpected error happened during updating enrollment: %s', e)
            raise InternalServerError()

        if args['RequestType'] == RequestType_MemberSubmission:
            self._memberSubmission_post_update(token, form, args)
        elif args['RequestType'] == RequestType_SaveFormData:
            self._saveFormData_post_update(token, form, args)
        elif args['RequestType'] == RequestType_EmployerSubmission:
            self._employerSubmission_post_update(token, form, args)
        elif args['RequestType'] == RequestType_ApprovalConfirmation:
            self._approvalConfirmation_post_update(token, form, args)
        elif args['RequestType'] == RequestType_Reject:
            self._reject_post_update(token, form, args)
        else:
            raise BadRequest('Unkown RequestType')

        return form

    def _memberSubmission_pre_update(self, token, form, args):
        if token is None:
            raise NotFound('Token was not found')

        if token.PendingFrom != 'Member' or token.TokenStatus != 'Active' or token.FormStatus != 'Pending':
            raise NotFound('Token was not Found or is not Active')

    def _memberSubmission_post_update(self, token, form, args):
        newToken = Token(
            FormID=token.FormID,
            FormType=token.FormType,
            InitiatedBy=token.InitiatedBy,
            InitiatedDate=datetime.utcnow(),
            FormStatus='Pending',
            PendingFrom='Employer',
            TokenStatus='Active',
            EmployerID=token.EmployerID,
            OlderTokenID=token.TokenID,
            LastModifiedDate=datetime.utcnow(),
        )

        db.session.add(newToken)
        token.FormStatus = 'Submitted'
        token.TokenStatus = 'Inactive'
        token.LastModifiedDate = datetime.utcnow()

    def _saveFormData_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'IpAddress' not in args or 'Username' not in args:
            raise Unauthorized()

        token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if token is None:
            raise NotFound()

        if token.PendingFrom != 'Employer' or token.TokenStatus != 'Active' or token.FormStatus != 'Pending':
            raise NotFound('Token was not Found or is not Active')

    def _saveFormData_post_update(self, token, form, args):
        pass

    def _employerSubmission_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'IpAddress' not in args or 'Username' not in args:
            raise Unauthorized()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth['role'] != ROLES_EMPLOYER:
            raise Unauthorized()

        if token is None or form is None:
            raise NotFound()

        if token.PendingFrom != 'Employer' or token.TokenStatus != 'Active' or token.FormStatus != 'Pending':
            raise NotFound('Token was not Found or is not Active')

    def _employerSubmission_post_update(self, token, form, args):
        form.PendingFrom = 'ReviewerManager'
        token.PendingFrom = 'ReviewerManager'
        token.LastModifiedDate = datetime.utcnow()
        db.session.commit()

    def _approvalConfirmation_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'IpAddress' not in args or 'Username' not in args:
            raise Unauthorized()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth['role'] != ROLES_REVIEW_MANAGER:
            raise Unauthorized()

        if token is None or form is None:
            raise NotFound()

        if token.PendingFrom != 'ReviewerManager' or token.TokenStatus != 'Active' or token.FormStatus != 'Pending':
            raise NotFound('Token was not Found or is not Active')

    def _approvalConfirmation_post_update(self, token, form, args):
        token.FormStatus = 'Approved'
        db.session.commit()

        subject = 'Your Enrollment has been approved'
        send_email(to_address=form.EmailAddress, subject=subject,
                   template='enrollment_approval_confirmation_to_member.html')

    def _reject_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'IpAddress' not in args or 'Username' not in args:
            raise Unauthorized()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth['role'] != ROLES_REVIEW_MANAGER:
            raise Unauthorized()

        if token is None or form is None:
            raise NotFound()

        if token.PendingFrom != 'ReviewerManager' or token.TokenStatus != 'Active' or token.FormStatus != 'Pending':
            raise NotFound('Token was not Found or is not Active')

    def _reject_post_update(self, token, form, args):
        token.FormStatus = 'Rejected'
        db.session.commit()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])
        if 'RejectionReason' in args and args['RejectionReason'] != '':
            comment = Comments(
                FormID=form.FormID,
                Role=auth['role'],
                Comment=args['RejectionReason'],
                Date=datetime.utcnow(),
            )

            db.session.add(comment)
            db.session.commit()

        subject = 'Your Enrollment has been rejected'
        send_email(to_address=form.EmailAddress, subject=subject, template='enrollment_rejected_to_member.html')
