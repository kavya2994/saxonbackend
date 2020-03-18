import argparse
import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, fields, inputs, cors
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from werkzeug.utils import secure_filename

from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models.comments import Comments
from ...models.roles import *
from ...models import db, status
from ...models.status import *
from ...api import api
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

RequestType_MemberSubmission = 'MemberSubmission'
RequestType_SaveFormData = 'SaveFormData'
RequestType_EmployerSubmission = 'EmployerSubmission'
RequestType_ApprovalConfirmation = 'ApprovalConfirmation'
RequestType_Reject = 'Rejected'


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


getParser = reqparse.RequestParser()
getParser.add_argument('Authorization', type=str, location='headers', required=False)
getParser.add_argument('username', type=str, location='headers', required=False)
getParser.add_argument('Ipaddress', type=str, location='headers', required=False)

deleteParser = reqparse.RequestParser()
deleteParser.add_argument('Authorization', type=str, location='headers', required=False)
deleteParser.add_argument('username', type=str, location='headers', required=False)
deleteParser.add_argument('Ipaddress', type=str, location='headers', required=False)

parser = reqparse.RequestParser()

parser.add_argument('Authorization', type=str, location='headers', required=False)
parser.add_argument('username', type=str, location='headers', required=False)
parser.add_argument('Ipaddress', type=str, location='headers', required=False)

parser.add_argument('RequestType', type=str, location='form', required=True,
                    help=f"Valid Values: [{RequestType_MemberSubmission}, {RequestType_SaveFormData}, {RequestType_EmployerSubmission}, {RequestType_ApprovalConfirmation}, {RequestType_Reject}]")
parser.add_argument('FirstName', type=str, location='form', required=False)
parser.add_argument('MiddleName', type=str, location='form', required=False)
parser.add_argument('LastName', type=str, location='form', required=False)
parser.add_argument('DOB', type=inputs.date_from_iso8601, location='form', required=False)
parser.add_argument('Title', type=str, location='form', required=False)
parser.add_argument('MaritalStatus', type=str, location='form', required=False)
parser.add_argument('MailingAddress', type=str, location='form', required=False)
parser.add_argument('AddressLine2', type=str, location='form', required=False)
parser.add_argument('District', type=str, location='form', required=False)
parser.add_argument('PostalCode', type=str, location='form', required=False)
parser.add_argument('Country', type=str, location='form', required=False)
parser.add_argument('EmailAddress', type=str, location='form', required=False)
parser.add_argument('Telephone', type=str, location='form', required=False)
parser.add_argument('StartDateofContribution', type=inputs.date_from_iso8601, location='form', required=False,
                    help='iso8601 format. eg: 2012-11-25')
parser.add_argument('StartDateofEmployment', type=inputs.date_from_iso8601, location='form', required=False,
                    help='iso8601 format. eg: 2012-11-25')
parser.add_argument('ConfirmationStatus', type=str, location='form', required=False)
parser.add_argument('EstimatedAnnualIncomeRange', type=str, location='form', required=False)
parser.add_argument('ImmigrationStatus', type=str, location='form', required=False)
parser.add_argument('SpouseName', type=str, location='form', required=False)
parser.add_argument('SpouseDOB', type=inputs.date_from_iso8601, location='form', required=False)
parser.add_argument('EmployerName', type=str, location='form', required=False)
parser.add_argument('EmployerID', type=str, location='form', required=False)
parser.add_argument('MemberID', type=str, location='form', required=False)
parser.add_argument('NewMemberID', type=str, location='form', required=False)
parser.add_argument('SignersName', type=str, location='form', required=False)
parser.add_argument('Signature', type=str, location='form', required=False)
parser.add_argument('RejectionReason', type=str, location='form', required=False)
parser.add_argument('MaidenName', type=str, location='form', required=False)
parser.add_argument('isExistingMember', type=str2bool, location='form', required=False)
parser.add_argument('file', type=FileStorage, location='files', required=False)
parser.add_argument('Comment', type=str, location='form', required=False)
parser.add_argument('CommentName', type=str, location='form', required=False)
parser.add_argument('CommentRole', type=str, location='form', required=False)
parser.add_argument('Signature', type=str, location='form', required=False)
parser.add_argument('SignatureType', type=str, location='form', required=False)

comments_model = ns.model('Comments', {
    "Name": fields.String,
    "Date": fields.String,
    "Comment": fields.String
})

response_model = ns.model('GetEnrollmentController', {
    "tokenID": fields.String,
    "employername": fields.String,
    "employernumber": fields.String,
    "formType": fields.String,
    "formCreatedDate": fields.String,
    "isExistingMember": fields.Boolean,
    "memberfirstName": fields.String,
    "memberLastName": fields.String,
    "title": fields.String,
    "maidenName": fields.String,
    "dob": fields.Date,
    "address": fields.String,
    "addressLine2": fields.String,
    "district": fields.String,
    "postalcode": fields.String,
    "country": fields.String,
    "email": fields.String,
    "phoneNumber": fields.String,
    "incomerange": fields.String,
    "immigrationstatus": fields.String,
    "comments": fields.List(fields.Nested(comments_model)),
    "maritalstatus": fields.String,
    "middlename": fields.String,
    "status": fields.String,
    "pendingFrom": fields.String,
    "startemployment": fields.Date,
    "startdate": fields.Date,
    "spouse_name": fields.String,
    "spouse_dob": fields.String,
    "member_id": fields.String,
    "filename": fields.String,
    "Signature": fields.String,
    "SignatureType": fields.String
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
        enrollmentform = None
        comments = None
        comments_list = []

        if token is None:
            raise BadRequest()
        if token.TokenStatus != STATUS_ACTIVE:
            raise NotFound("Not a valid token")
        if token.PendingFrom != ROLES_MEMBER and token.TokenStatus == status.STATUS_ACTIVE:
            auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

            if not auth['role'] in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
                raise Unauthorized()
        try:
            enrollmentform = Enrollmentform.query.get(token.FormID)
            comments = Comments.query.filter(Comments.FormID == token.FormID, Comments.FormType == "Enrollment") \
                .order_by(Comments.CommentsID.desc()).all()
        except Exception as e:
            LOG.warning('Unexpected error happened during handling enrollment: %s', e)
            raise InternalServerError()

        if enrollmentform is None:
            raise UnprocessableEntity("Can't find enrollment form")

        if comments is not None:
            for comment in comments:
                comments_list.append({
                    "Name": comment.Name,
                    "Date": comment.Date,
                    "Comment": comment.Comment
                })

        return {
                   "tokenID": TokenID,
                   "employername": enrollmentform.EmployerName,
                   "employernumber": enrollmentform.EmployerID,
                   "formType": 'Enrollment',
                   "formCreatedDate": enrollmentform.InitiatedDate,
                   "isExistingMember": enrollmentform.AlreadyEnrolled,
                   "memberfirstName": enrollmentform.FirstName,
                   "memberLastName": enrollmentform.LastName,
                   "title": enrollmentform.Title,
                   "maidenName": enrollmentform.MaidenName,
                   "dob": enrollmentform.DOB,
                   "address": enrollmentform.MailingAddress,
                   "addressLine2": enrollmentform.AddressLine2,
                   "district": enrollmentform.District,
                   "postalcode": enrollmentform.PostalCode,
                   "country": enrollmentform.Country,
                   "email": enrollmentform.EmailAddress,
                   "phoneNumber": enrollmentform.Telephone,
                   "incomerange": enrollmentform.EstimatedAnnualIncomeRange,
                   "immigrationstatus": enrollmentform.ImmigrationStatus,
                   "comments": comments_list,
                   "maritalstatus": enrollmentform.MaritalStatus,
                   "middlename": enrollmentform.MiddleName,
                   "status": enrollmentform.Status,
                   "pendingFrom": enrollmentform.PendingFrom,
                   "startemployment": enrollmentform.StartDateofEmployment,
                   "startdate": enrollmentform.StartDateofContribution,
                   "spouse_name": enrollmentform.SpouseName,
                   "spouse_dob": enrollmentform.SpouseDOB,
                   "member_id": enrollmentform.OldMemberID,
                   "filename": str(enrollmentform.FilePath).replace("/", "\\").split("\\")[
                       len(str(enrollmentform.FilePath).replace("/", "\\").split(
                           "\\")) - 1] if enrollmentform.FilePath is not None else "",
                   "Signature": enrollmentform.Signature,
                   "SignatureType": enrollmentform.SignatureType,
                   "NewMemberID": enrollmentform.MemberID
               }, 200

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

        form = Enrollmentform.query.get(token.FormID)
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
            form.AlreadyEnrolled = args["isExistingMember"]
            form.OldMemberID = args["MemberID"]
            form.MaidenName = args["MaidenName"]
            form.MemberID = args["NewMemberID"]
            if args['RequestType'] != 'MemberSubmission':
                if 'EmployerName' in args:
                    form.EmployerName = args['EmployerName']

                if 'EmployerID' in args:
                    form.EmployerID = args['EmployerID']

            db.session.commit()
        except Exception as e:
            LOG.warning('Unexpected error happened during updating enrollment: %s', e)
            raise InternalServerError()

        if args['RequestType'] == RequestType_MemberSubmission:
            self._memberSubmission_post_update(token, form, args)
            return RESPONSE_OK
        elif args['RequestType'] == RequestType_SaveFormData:
            self._saveFormData_post_update(token, form, args)
        elif args['RequestType'] == RequestType_EmployerSubmission:
            self._employerSubmission_post_update(token, form, args)
            return RESPONSE_OK
        elif args['RequestType'] == RequestType_ApprovalConfirmation:
            self._approvalConfirmation_post_update(token, form, args)
            return RESPONSE_OK
        elif args['RequestType'] == RequestType_Reject:
            self._reject_post_update(token, form, args)
            return RESPONSE_OK
        else:
            raise BadRequest('Unkown RequestType')

        return RESPONSE_OK

    def _memberSubmission_pre_update(self, token, form, args):
        if token is None:
            raise NotFound('Token was not found')

        if token.PendingFrom != ROLES_MEMBER or token.TokenStatus != STATUS_ACTIVE or token.FormStatus != STATUS_PENDING:
            raise NotFound('Token was not Found or is not Active')
        if form.Signature is None and args["Signature"] is None:
            raise BadRequest("Signature is needed for Submission")
        if 'file' in request.files and form.FilePath is None:
            path = APP.config['DATA_DIR']
            file = request.files['file']
            filename = secure_filename(file.filename)
            path = os.path.join(path, "Employers")
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, token.EmployerID)
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, "enrollment")
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, str(token.TokenID))
            if not os.path.exists(path):
                os.mkdir(path)
            file.save(os.path.join(path, filename))
            form.FilePath = os.path.join(path, filename)

    def _memberSubmission_post_update(self, token, form, args):
        newToken = Token(
            FormID=token.FormID,
            FormType=token.FormType,
            InitiatedBy=token.InitiatedBy,
            InitiatedDate=datetime.utcnow(),
            FormStatus=STATUS_PENDING,
            PendingFrom=ROLES_EMPLOYER,
            TokenStatus=STATUS_ACTIVE,
            EmployerID=token.EmployerID,
            OlderTokenID=token.TokenID,
            LastModifiedDate=datetime.utcnow(),
        )

        db.session.add(newToken)
        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
            comment = Comments(
                FormID=form.FormID,
                Name=args['CommentName'],
                Role=ROLES_MEMBER,
                Comment=args['Comment'],
                Date=datetime.utcnow(),
                FormType="Enrollment"
            )
            db.session.add(comment)
            db.session.commit()
        token.FormStatus = STATUS_SUBMIT
        token.TokenStatus = STATUS_INACTIVE
        token.LastModifiedDate = datetime.utcnow()
        if form.Signature is None:
            form.Signature = args["Signature"]
            form.SignatureType = args["SignatureType"]
        form.PendingFrom = ROLES_EMPLOYER
        form.Status = STATUS_PENDING
        db.session.commit()
        name = form.FirstName + " " + form.LastName
        subject = 'Your Enrollment has been submitted'
        body = f'<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>' + \
               f'<p>Dear {name}</p>' + \
               f'<p>Your Enrollment was submitted on {datetime.utcnow().strftime("%Y-%m-%d")} ' + \
               f'You will receive notification once your form has been processed.</p>'
        send_email(to_address=form.EmailAddress, subject=subject, body=body)

    def _saveFormData_pre_update(self, token, form, args):

        if token is None:
            raise NotFound()
        if token.PendingFrom == ROLES_MEMBER and token.TokenStatus == status.STATUS_ACTIVE:
            return
        if 'Authorization' not in args or 'Ipaddress' not in args or 'username' not in args:
            raise Unauthorized()
        decoded_token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])
        if not decoded_token["role"] in [ROLES_HR, ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()

        if token.TokenStatus != STATUS_ACTIVE or token.FormStatus != STATUS_PENDING:
            raise NotFound('Token was not Found or is not Active')

    def _saveFormData_post_update(self, token, form, args):
        if 'file' in request.files and form.FilePath is None:
            path = APP.config['DATA_DIR']
            file = request.files['file']
            filename = secure_filename(file.filename)
            path = os.path.join(path, "Employers")
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, token.EmployerID)
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, "enrollment")
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, str(token.TokenID))
            if not os.path.exists(path):
                os.mkdir(path)
            file.save(os.path.join(path, filename))
            form.FilePath = os.path.join(path, filename)
        form.Status = STATUS_PENDING
        if form.Signature is None:
            form.Signature = args["Signature"]
            form.SignatureType = args["SignatureType"]
        token.LastModifiedDate = datetime.utcnow()
        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
            comment = Comments(
                FormID=form.FormID,
                Name=args['CommentName'],
                Role=args['CommentRole'],
                Comment=args['Comment'],
                Date=datetime.utcnow(),
                FormType="Enrollment"
            )
            db.session.add(comment)
            db.session.commit()
        db.session.commit()
        pass

    def _employerSubmission_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'Ipaddress' not in args or 'username' not in args:
            raise Unauthorized()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth['role'] != ROLES_EMPLOYER:
            raise Unauthorized()

        if token is None or form is None:
            raise NotFound()

        if token.PendingFrom != ROLES_EMPLOYER or token.TokenStatus != STATUS_ACTIVE or token.FormStatus != STATUS_PENDING:
            raise NotFound('Token was not Found or is not Active')

    def _employerSubmission_post_update(self, token, form, args):
        form.PendingFrom = ROLES_REVIEW_MANAGER
        token.PendingFrom = ROLES_REVIEW_MANAGER
        token.LastModifiedDate = datetime.utcnow()
        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
            comment = Comments(
                FormID=form.FormID,
                Name=args['CommentName'],
                Role=args['CommentRole'],
                Comment=args['Comment'],
                Date=datetime.utcnow(),
                FormType="Enrollment"
            )
            db.session.add(comment)
            db.session.commit()
        db.session.commit()

    def _approvalConfirmation_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'Ipaddress' not in args or 'username' not in args:
            raise Unauthorized()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth['role'] != ROLES_REVIEW_MANAGER:
            raise Unauthorized()

        if token is None or form is None:
            raise NotFound()

        if token.PendingFrom != ROLES_REVIEW_MANAGER or token.TokenStatus != STATUS_ACTIVE or token.FormStatus != STATUS_PENDING:
            raise NotFound('Token was not Found or is not Active')
        if args["NewMemberID"] is None or args["NewMemberID"] == "":
            raise BadRequest("Please enter valid Member Number")

    def _approvalConfirmation_post_update(self, token, form, args):
        token.FormStatus = STATUS_APPROVE
        form.Status = STATUS_APPROVE
        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
            comment = Comments(
                FormID=form.FormID,
                Name=args['CommentName'],
                Role=ROLES_REVIEW_MANAGER,
                Comment=args['Comment'],
                Date=datetime.utcnow(),
                FormType="Enrollment"
            )
            db.session.add(comment)
            db.session.commit()
        db.session.commit()
        name = form.FirstName + " " + form.LastName
        subject = 'Your Enrollment has been approved'
        body = '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>' + \
               '<p>Dear ' + name + '</p>' + \
               '<p>Your Enrollment has been processed</p>'
        send_email(to_address=form.EmailAddress, subject=subject,
                   body=body)

    def _reject_pre_update(self, token, form, args):
        if 'Authorization' not in args or 'Ipaddress' not in args or 'username' not in args:
            raise Unauthorized()

        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth['role'] != ROLES_REVIEW_MANAGER:
            raise Unauthorized()

        if token is None or form is None:
            raise NotFound()

        if token.PendingFrom != ROLES_REVIEW_MANAGER or token.TokenStatus != STATUS_ACTIVE or token.FormStatus != STATUS_PENDING:
            raise NotFound('Token was not Found or is not Active')

    def _reject_post_update(self, token, form, args):
        token.FormStatus = status.STATUS_REJECT
        form.Status = STATUS_REJECT
        db.session.commit()
        if 'RejectionReason' in args and args['RejectionReason'] != '' and args['RejectionReason'] is not None:
            comment = Comments(
                FormID=form.FormID,
                Role=ROLES_REVIEW_MANAGER,
                Name=args["username"],
                Comment=args['RejectionReason'],
                Date=datetime.utcnow(),
                FormType="Enrollment"
            )

            db.session.add(comment)
            db.session.commit()
        name = form.FirstName + " " + form.LastName
        subject = 'Your Enrollment has been rejected'
        body = f'<p>**This is an auto-generated e-mail message.' + \
               f' Please do not reply to this message. **</p>' + \
               f'<p>Dear {name} </p>' + \
               f'<p>Your Enrollment has been rejected </p>' + \
               f'<p>Please click <a href="{APP.config["FRONTEND_URL"]}/enrollment-form/{token}">here</a>. ' \
               f'Otherwise, cut and paste the link below into a browser, ' + \
               f'fill in the required information, and when you are done hit the submit button to ' + \
               f'start your enrollment into the plan.</p>' + \
               f'<p>{args["RejectionReason"]}</p>' + \
               f'<p>-----------------------------------</p>' + \
               f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{token}</p>' + \
               f'<p>To learn more about the Silver Thatch Pension ' + \
               f'Plan, click <a href="{APP.config["MAIL_ENROLLMENT_URL"]}">here</a>' \
               f' to review our members handbook. </p>'
        send_email(to_address=form.EmailAddress, subject=subject, body=body)

    @ns.doc(description='Delete enrollment file',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(deleteParser, validate=True)
    # @ns.marshal_with()
    def delete(self, TokenID):
        args = deleteParser.parse_args(strict=True)

        token = Token.query.get(TokenID)
        if token is None:
            raise NotFound("Can't find the token")
        if token.PendingFrom == ROLES_MEMBER and token.TokenStatus == status.STATUS_ACTIVE:
            pass
        else:
            auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])
            if auth['role'] != ROLES_REVIEW_MANAGER:
                raise Unauthorized()
        enrollment = Enrollmentform.query.get(token.FormID)
        if os.path.exists(enrollment.FilePath):
            os.remove(enrollment.FilePath)
        enrollment.FilePath = None

        try:
            db.session.commit()
            return RESPONSE_OK
        except Exception as e:
            LOG.error("Exception while deleting the form", e)
            raise InternalServerError("Error while deleting the form. Please try again")
