import os
import jwt
import json
import smtplib
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, cors, fields
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token, TOKEN_FORMTYPE_ENROLLMENT
from ...models.comments import Comments
from ...models.roles import *
from ...models import db, status, roles
from ...api import api
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)

parser.add_argument('MemberEmail', type=str, location='json', required=True)
parser.add_argument('MemberFirstName', type=str, location='json', required=True)
parser.add_argument('Comment', type=str, location='json', required=False)
parser.add_argument('user', type=str, location='json', required=True)

response_model = ns.model('PostEnrollmentInitiationController', {
    'result': fields.String,
    'TokenID': fields.String,
})


@ns.route("/initiate")
class EnrollmentInitiationController(Resource):
    @ns.doc(description='Enrollment Initiation',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if auth["role"] not in [ROLES_EMPLOYER, ROLES_HR, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()

        try:
            employer_username = args['user']
            employer_id = employer_username
            initiation_date = datetime.utcnow()

            if str(employer_id)[-2:].__contains__("HR"):
                employer_username = str(employer_username)[:-2]

            new_enrollment = Enrollmentform(
                EmployerID=employer_username,
                InitiatedDate=initiation_date,
                FirstName=args["MemberFirstName"],
                EmailAddress=args["MemberEmail"],
                PendingFrom=roles.ROLES_MEMBER,
                Status=status.STATUS_PENDING
            )

            db.session.add(new_enrollment)
            db.session.commit()

            token_data = Token(

                # FormID=new_enrollment.FormID,
                # InitiatedBy=employer_username,
                # InitiatedDate=initiation_date,
                # FormStatus="Pending",
                # FormType="Enrollment",
                # PendingFrom='Member',
                # TokenStatus='Active',
                # EmployerID='',

                FormID=new_enrollment.FormID,
                InitiatedBy=args["username"],
                InitiatedDate=initiation_date,
                FormStatus=status.STATUS_PENDING,
                FormType=TOKEN_FORMTYPE_ENROLLMENT,
                PendingFrom=roles.ROLES_MEMBER,
                TokenStatus=status.STATUS_ACTIVE,
                EmployerID=employer_username,
                LastModifiedDate=datetime.utcnow(),

            )

            db.session.add(token_data)
            db.session.commit()

            if 'Comment' in args and args['Comment'] != '':
                comment = Comments(
                    FormID=new_enrollment.FormID,
                    Role=auth['role'],
                    Comment=args['Comment'],
                    Date=initiation_date,

                )
                db.session.add(comment)
                db.session.commit()

            email_subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"

            email_body = f"""
<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>
<p>Dear {args['MemberFirstName']}</p>
<p>Please click here. Otherwise, cut and paste the link below into a browser, fill in the
required information, and when you are done hit the submit button to start your enrollment
into the plan.</p><p>-----------------------------------------</p>
<p>{APP.config['SERVER_WEB_URL']}/enrollment-form/{token_data.TokenID}</p>
<p>To learn more about the Silver Thatch Pension Plan,
click here to review our members handbook. </p>"""

            send_email(to_address=args["MemberEmail"], subject=email_subject, body=email_body)

            return {
                "result": "Success",
                "TokenID": token_data.TokenID
            }

        except Exception as e:
            LOG.warning('Unexpected error happened initializing an enrollment: %s', e)
            raise InternalServerError
