import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify, token_verify_or_raise
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models.comments import Comments
from ...models.roles import *
from ...models import db
from ...api import api
from ...services.mail import send_email
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

parser.add_argument('MemberEmail', type=str, location='json', required=True)
parser.add_argument('MemberFirstName', type=str, location='json', required=True)
parser.add_argument('Comment', type=str, location='json', required=False)

@ns.route("/initiate")
class EnrollmentInitiation(Resource):
    @ns.doc(parser=parser,
        description='Enrollment Initiation',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args["Authorization"], ip=args["IpAddress"], user=args["Username"])

        if auth["Role"] != ROLES_EMPLOYER:
            raise Unauthorized()

        try:
            employer_username = auth['Username']
            initiation_date = datetime.utcnow()

            # if str(employer_id)[-2:].__contains__("HR"):
            #     employer_username = str(employer_username)[:-2]

            new_enrollment = Enrollmentform(
                EmployerID=employer_username,
                InitiatedDate=initiation_date,
                FirstName=args["MemberFirstName"],
                EmailAddress=args["MemberEmail"],
            )

            db.session.add(new_enrollment)
            db.session.commit()

            token_data = Token(
                FormID = new_enrollment.FormID,
                InitiatedBy = employer_username,
                InitiatedDate = initiation_date,
                FormStatus = "Pending",
                FormType = "Enrollment",
                PendingFrom = 'Member',
                TokenStatus = 'Active',
                EmployerID = '',
            )

            db.session.add(token_data)
            db.session.commit()

            if 'Comment' in args and args['Comment'] != '':
                comment = Comments(
                    FormID = new_enrollment.FormID,
                    Role = auth['Role'],
                    Comment = args['Comment'],
                    Date = initiation_date,
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
<p>{app.config['SERVER_WEB_URL']}/enrollment-form/{token_data.TokenID}</p>
<p>To learn more about the Silver Thatch Pension Plan,
click here to review our members handbook. </p>"""

            send_email(to_address=args["MemberEmail"], subject=email_subject, body=email_body)

            return {
                    "result": "Success",
                    "TokenID": token_data.TokenID
                }

        except Exception as e:
            print(str(e))
            raise InternalServerError
