import json
import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from werkzeug.utils import secure_filename

from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models import db, status, roles
from ...models.terminationform import Terminationform
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
import smtplib
from . import ns
from ... import APP, LOG

RequestType_MemberSubmission = 'MemberSubmission'
RequestType_SaveFormData = 'SaveFormData'
RequestType_EmployerSubmission = 'EmployerSubmission'
RequestType_ApprovalConfirmation = 'ApprovalConfirmation'
RequestType_Reject = 'Reject'

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=False)
parser.add_argument('username', type=str, location='headers', required=False)
parser.add_argument('Ipaddress', type=str, location='headers', required=False)

parser.add_argument("request_type", type=str, location='form', required=True)
parser.add_argument('MemberName', type=str, location='form', required=False)
parser.add_argument('employerusername', type=str, location='form', required=False)
parser.add_argument('MemberNumber', type=str, location='form', required=False)
parser.add_argument('EmailAddress', type=str, location='form', required=False)
parser.add_argument('FinalDateOfEmployment', type=inputs.date_from_iso8601, location='form', required=False)
parser.add_argument('ReasonforTermination', type=str, location='form', required=False)
parser.add_argument('role', type=str, location='form', required=False)
parser.add_argument('LastDeduction', type=str, location='form', required=False)
parser.add_argument('Address', type=str, location='form', required=False)
parser.add_argument('AddressLine2', type=str, location='form', required=False)
parser.add_argument('District', type=str, location='form', required=False)
parser.add_argument('PostalCode', type=str, location='form', required=False)
parser.add_argument('Country', type=str, location='form', required=False)
parser.add_argument('EstimatedAnnualIncomeRange', type=str, location='form', required=False)
parser.add_argument('Status', type=str, location='form', required=False)
parser.add_argument('PhoneNumber', type=str, location='form', required=False)
parser.add_argument('Comment', type=str, location='form', required=False)
parser.add_argument('CommentName', type=str, location='form', required=False)
parser.add_argument('PendingFrom', type=str, location='form', required=False)
parser.add_argument('Signature', type=str, location='form', required=False)
parser.add_argument('SignatureType', type=str, location='form', required=False)

response_model = ns.model('PostTerminationInitiationController', {
    'result': fields.String,
})


@ns.route("/token/<TokenID>")
class TerminationInitiationController(Resource):
    @ns.doc(description='',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self, TokenID):
        args = parser.parse_args()
        decode_token = None
        if not (args["request_type"] == RequestType_MemberSubmission or
                args["request_type"] == RequestType_SaveFormData):
            print(args["request_type"])
            decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                                 user=args['username'])
        print("decode_token------", decode_token)
        # if decode_token['role'] != ROLES_EMPLOYER:
        #     raise Unauthorized()
        initiation_date = datetime.utcnow()
        request_type = args["request_type"]
        employer_id = args['employerusername']
        employernumber = employer_id

        # args["formCreatedDate"] = datetime.utcnow()
        if str(employer_id)[-2:].__contains__("HR"):
            employernumber = str(employer_id)[:-2]

        token = Token.query.filter_by(TokenID=TokenID).first()
        form_id = token.FormID
        if token.TokenStatus == status.STATUS_ACTIVE:
            form = Terminationform.query.filter_by(FormID=form_id).first()

            if form is not None:
                member_name = form.MemberName
                if request_type == RequestType_SaveFormData:
                    # form.MemberName = args['MemberName'],
                    # form.MemberNumber = args['MemberNumber'],
                    form.EmailAddress = args['EmailAddress']
                    form.FinalDateOfEmployment = args['FinalDateOfEmployment']
                    form.ReasonforTermination = args['ReasonforTermination']
                    form.LastDeduction = args['LastDeduction']
                    form.Address = args['Address']
                    form.AddressLine2 = args['AddressLine2']
                    form.District = args['District']
                    form.PostalCode = args['PostalCode']
                    form.Country = args['Country']
                    form.EstimatedAnnualIncomeRange = args['EstimatedAnnualIncomeRange']
                    # form.Status = args['Status']
                    # form.PendingFrom = args['PendingFrom']
                    form.PhoneNumber = args["PhoneNumber"]

                    # token.FormStatus = status.STATUS_PENDING
                    # token.PendingFrom = args['PendingFrom']
                    if form.Signature is not None:
                        form.Signature = args["Signature"]
                        form.SignatureType = args["SignatureType"]
                    token.LastModifiedDate = datetime.utcnow()

                    db.session.commit()
                    if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                        comment = Comments(
                            FormID=form_id,
                            Name=args['CommentName'],
                            Role=args['role'],
                            Comment=args['Comment'],
                            Date=initiation_date,
                            FormType="Termination"
                        )
                        db.session.add(comment)
                        db.session.commit()

                    return {"result": "Success"}, 200
                elif request_type == RequestType_MemberSubmission:
                    if args["EmailAddress"] is None or args["EmailAddress"] == '':
                        LOG.error("No email address for tokenid", TokenID)
                        raise UnprocessableEntity("Please provide a valid Email address")
                    form.EmailAddress = args['EmailAddress']
                    form.FinalDateOfEmployment = args['FinalDateOfEmployment']
                    form.ReasonforTermination = args['ReasonforTermination']
                    form.LastDeduction = args['LastDeduction']
                    form.Address = args['Address']
                    form.AddressLine2 = args['AddressLine2']
                    form.District = args['District']
                    form.PostalCode = args['PostalCode']
                    form.Country = args['Country']
                    form.EstimatedAnnualIncomeRange = args['EstimatedAnnualIncomeRange']
                    form.Status = status.STATUS_PENDING
                    form.PendingFrom = roles.ROLES_EMPLOYER
                    form.PhoneNumber = args["PhoneNumber"]

                    token.FormStatus = status.STATUS_PENDING
                    token.LastModifiedDate = datetime.utcnow()
                    token.PendingFrom = roles.ROLES_EMPLOYER
                    token.TokenStatus = status.STATUS_INACTIVE
                    if form.Signature is not None:
                        form.Signature = args["Signature"]
                        form.SignatureType = args["SignatureType"]

                    new_token = Token(FormID=form.FormID,
                                      EmployerID=token.EmployerID,
                                      InitiatedBy=token.InitiatedBy,
                                      InitiatedDate=initiation_date,
                                      FormStatus=status.STATUS_PENDING,
                                      FormType=TOKEN_FORMTYPE_TERMINATION,
                                      PendingFrom=roles.ROLES_EMPLOYER,
                                      TokenStatus=status.STATUS_ACTIVE,
                                      LastModifiedDate=datetime.utcnow(),
                                      OlderTokenID=TokenID
                                      )
                    db.session.add(new_token)

                    if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                        comment = Comments(
                            FormID=form_id,
                            Name=args['CommentName'],
                            Role=args['role'],
                            Comment=args['Comment'],
                            Date=initiation_date,
                            FormType="Termination"
                        )
                        db.session.add(comment)
                    db.session.commit()
                    try:
                        member_subject = 'Please complete your Silver Thatch Pensions Employment Termination Form'
                        member_msg_text = (
                            '<p>**This is an auto-generated e-mail message.'
                            ' Please do not reply to this message. **</p>'
                            f'<p>Dear {member_name}</p>'
                            f'<p>Your termination was submitted on {datetime.utcnow().strftime("%Y-%m-%d")}. '
                            'You will receive notification once your form has been processed</p>'
                        )

                        send_email(to_address=args['EmailAddress'], subject=member_subject, body=member_msg_text)
                        return {"result": "Success"}, 200
                    except smtplib.SMTPException as e:
                        LOG.error("smtp exception at termination", str(e))
                        raise InternalServerError("Cannot send email at the moment")

                elif request_type == RequestType_EmployerSubmission:
                    if decode_token is not None and decode_token["role"] in [roles.ROLES_EMPLOYER, roles.ROLES_HR]:
                        form.EmailAddress = args['EmailAddress']
                        form.FinalDateOfEmployment = args['FinalDateOfEmployment']
                        form.ReasonforTermination = args['ReasonforTermination']
                        form.LastDeduction = args['LastDeduction']
                        form.Address = args['Address']
                        form.AddressLine2 = args['AddressLine2']
                        form.District = args['District']
                        form.PostalCode = args['PostalCode']
                        form.Country = args['Country']
                        form.EstimatedAnnualIncomeRange = args['EstimatedAnnualIncomeRange']
                        form.Status = status.STATUS_PENDING
                        form.PendingFrom = roles.ROLES_REVIEW_MANAGER

                        token.EmployerID = employernumber
                        token.LastModifiedDate = datetime.utcnow()
                        token.PendingFrom = roles.ROLES_REVIEW_MANAGER
                        token.TokenStatus = status.STATUS_ACTIVE
                        token.FormStatus = status.STATUS_PENDING
                        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                            comment = Comments(
                                FormID=form_id,
                                Name=args['CommentName'],
                                Role=args['role'],
                                Comment=args['Comment'],
                                Date=initiation_date,
                                FormType="Termination"
                            )
                            db.session.add(comment)
                        db.session.commit()
                        return {"result": "Success"}, 200
                    else:
                        raise Unauthorized()
                elif request_type == RequestType_ApprovalConfirmation:
                    if decode_token is not None and decode_token['role'] == roles.ROLES_REVIEW_MANAGER:
                        if args["EmailAddress"] is None or args["EmailAddress"] == '':
                            LOG.error("No email address for tokenid", TokenID)
                            raise UnprocessableEntity("Please provide a valid Email address")
                        token.FormStatus = status.STATUS_APPROVE
                        form.Status = status.STATUS_APPROVE
                        token.LastModifiedDate = datetime.utcnow()
                        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                            comment = Comments(
                                FormID=form_id,
                                Name=args['CommentName'],
                                Role=args['role'],
                                Comment=args['Comment'],
                                Date=initiation_date,
                                FormType="Termination"
                            )
                            db.session.add(comment)
                        db.session.commit()
                        try:
                            subject = 'Silver Thatch Pensions Employment Termination Form'
                            msg_text = '<p>**This is an auto-generated e-mail message.' + \
                                       ' Please do not reply to this message. **</p>' + \
                                       f'<p>Dear {member_name}</p>' + \
                                       '<p>Your termination has been processed </p>'

                            send_email(to_address=args['EmailAddress'], subject=subject, body=msg_text)
                            return {"result": "Success"}, 200
                        except smtplib.SMTPException as e:
                            LOG.error("smtp exception at termination", str(e))
                            raise InternalServerError("Cannot send email at the moment")
                elif request_type == RequestType_Reject:
                    if decode_token is not None and decode_token['role'] == roles.ROLES_REVIEW_MANAGER:
                        if args["EmailAddress"] is None or args["EmailAddress"] == '':
                            LOG.error("No email address for tokenid", TokenID)
                            raise UnprocessableEntity("Please provide a valid Email address")

                        token.FormStatus = status.STATUS_REJECT
                        form.Status = status.STATUS_REJECT
                        token.LastModifiedDate = datetime.utcnow()
                        if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                            comment = Comments(
                                FormID=form_id,
                                Name=args['CommentName'],
                                Role=args['role'],
                                Comment=args['Comment'],
                                Date=initiation_date,
                                FormType="Termination"
                            )
                            db.session.add(comment)
                        db.session.commit()
                        try:
                            subject = 'Silver Thatch Pensions Employment Termination Form'
                            msg_text = '<p>**This is an auto-generated e-mail message.' + \
                                       ' Please do not reply to this message. **</p>' + \
                                       f'<p>Dear {member_name}</p>' + \
                                       '<p>Your Termination has been rejected </p>' + \
                                       '<p>Please click here. Otherwise, cut and paste the link below into a ' + \
                                       'browser, ' + \
                                       'fill in the required information, and when you are done hit the ' + \
                                       'submit button to ' + \
                                       'start your termination into the plan.</p>' + \
                                       '<p>-----------------------------------------------------</p>' + \
                                       f'<p>{APP.config["FRONTEND_URL"]}/terminationform/{token} </p>' + \
                                       '<p>To learn more about the Silver Thatch Pension ' + \
                                       'Plan, click here to review our members handbook. </p>'

                            send_email(to_address=args['EmailAddress'], subject=subject, body=msg_text)
                            return {"result": "Success"}, 200
                        except smtplib.SMTPException as e:
                            LOG.error("smtp exception at termination", str(e))
                            raise InternalServerError("Cannot send email at the moment")
                else:
                    raise UnprocessableEntity("Not a valid request")
