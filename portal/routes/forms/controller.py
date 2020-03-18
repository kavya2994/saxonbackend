import os
import jwt
import json
import smtplib
from functools import reduce
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request
from smtplib import SMTPException
from flask_restx import Resource, reqparse, fields, inputs, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models.beneficiary import Beneficiary
from ...models.contributionform import Contributionform
from ...models.enrollmentform import Enrollmentform
from ...models.roles import *
from ...models.status import *
from ...models import db
from ...api import api
from . import ns
from ... import APP, LOG
from ...models.terminationform import Terminationform
from ...models.token import Token
from ...services.mail import send_email

postParser = reqparse.RequestParser()
postParser.add_argument('Authorization', type=str, location='headers', required=True)
postParser.add_argument('username', type=str, location='headers', required=True)
postParser.add_argument('Ipaddress', type=str, location='headers', required=True)
postParser.add_argument('EmailID', type=str, location='json', required=True)

deleteParser = reqparse.RequestParser()
deleteParser.add_argument('Authorization', type=str, location='headers', required=True)
deleteParser.add_argument('username', type=str, location='headers', required=True)
deleteParser.add_argument('Ipaddress', type=str, location='headers', required=True)
deleteParser.add_argument('FormType', type=str, location='json', required=True)

response_model_ok = ns.model('DeleteBeneficiaryFormController', {
    "result": fields.String,
})


@ns.route("/token/<TokenID>")
class FormController(Resource):
    @ns.doc(description='Delete Form',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(deleteParser, validate=True)
    @ns.marshal_with(response_model_ok)
    def delete(self, TokenID):
        args = deleteParser.parse_args(strict=True)
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] not in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        if args["FormType"] == "Contribution":
            if auth['role'] != ROLES_REVIEW_MANAGER:
                raise Unauthorized()
            form = Contributionform.query.get(TokenID)
            form.Status = STATUS_DELETE
            db.session.commit()
            return RESPONSE_OK
        token = Token.query.get(TokenID)
        if token is None:
            raise NotFound("Can't find the token")

        if auth['role'] == ROLES_REVIEW_MANAGER or (
                auth['role'] == ROLES_EMPLOYER and token.PendingFrom == ROLES_MEMBER):
            pass

        token.TokenStatus = STATUS_DELETE
        if token.FormType == "Enrollment":
            form = Enrollmentform.query.get(token.FormID)
            form.Status = STATUS_DELETE
        elif token.FormType == "Termination":
            form = Terminationform.query.get(token.FormID)
            form.Status = STATUS_DELETE
        else:
            raise BadRequest("Can't delete")
        try:
            db.session.commit()
            return RESPONSE_OK
        except Exception as e:
            LOG.error("Exception while deleting the form", e)
            raise InternalServerError("Error while deleting the form. Please try again")

    @ns.doc(description='Send mail as a remainder',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(postParser, validate=True)
    @ns.marshal_with(response_model_ok)
    def post(self, TokenID):
        args = postParser.parse_args(strict=True)
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] not in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()

        token = Token.query.get(TokenID)
        if token is None:
            raise NotFound("Can't find the token")

        if token.TokenStatus != STATUS_ACTIVE or token.PendingFrom != ROLES_MEMBER:
            raise BadRequest("Can't send mail")
        email_id = args["EmailID"]
        if token.FormType == "Enrollment":
            form = Enrollmentform.query.get(token.FormID)
            name = str(form.FirstName if form.FirstName is not None else "") + " " + str(form.LastName if form.LastName is not None else "")
            subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
            msgtext = f'<p>**This is an auto-generated e-mail message.' + \
                      f' Please do not reply to this message. **</p>' + \
                      f'<p>Dear{name}</p>' + \
                      f'<p>Please click <a href="{APP.config["FRONTEND_URL"]}/enrollment-form/{TokenID}">here</a>' \
                      f'. Otherwise, ' + \
                      f'cut and paste the link below into a browser, fill in the ' + \
                      f'required information, and when you are done' + \
                      f' hit the submit button to start your enrollment ' + \
                      f'into the plan.</p>' + \
                      f'<p>Have you had a chance to look at this yet?</p>' + \
                      f'<p>-----------------------------------------</p>' + \
                      f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{TokenID}</p>' + \
                      f'<p>To learn more about the Silver Thatch Pension Plan,' \
                      f'click <a href="{APP.config["MAIL_ENROLLMENT_URL"]}">here</a>' \
                      f'to review our members handbook. </p>'
            try:
                send_email(to_address=email_id, subject=subject, body=msgtext)
                form.LastNotifiedDate = datetime.utcnow()
                db.session.commit()
                return RESPONSE_OK
            except SMTPException as e:
                LOG.error("Exception while sending mail in remainder enrollment form", e)
                raise InternalServerError("Can't notify the user please enter a valid email id")
            except Exception as e:
                LOG.error("Exception while reminding enrollment form", e)
                raise InternalServerError("Can't notify the user")
        elif token.FormType == "Termination":
            form = Terminationform.query.get(token.FormID)
            name = form.MemberName
            subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
            msgtext = '<p>**This is an auto-generated e-mail message.' + \
                      ' Please do not reply to this message. **</p>' + \
                      '<p>Dear ' + name + '</p>' + \
                      '<p>In an effort to keep you connected with your Silver Thatch Pension ' + \
                      'after you leave your current position, please click here or copy the link ' + \
                      'below into a browser to complete the termination of employment form. This ' + \
                      'form notifies us that you are no longer employed with your current ' + \
                      'employer and allows Silver Thatch Pensions to stay in touch with you in ' + \
                      'regards to your pension. </p> ' + \
                      '<p>Have you had a chance to look at this yet?</p>' + \
                      '<p>-----------------------------------------</p>' + \
                      '<p>' + APP.config["FRONTEND_URL"] + '/terminationform/' + TokenID + '</p>'
            try:
                send_email(to_address=email_id, subject=subject, body=msgtext)
                form.LastNotifiedDate = datetime.utcnow()
                db.session.commit()
                return RESPONSE_OK
            except SMTPException as e:
                LOG.error("Exception while sending mail in remainder enrollment form", e)
                raise InternalServerError("Can't notify the user")
            except Exception as e:
                LOG.error("Exception while reminding enrollment form", e)
                raise InternalServerError("Can't notify the user")
