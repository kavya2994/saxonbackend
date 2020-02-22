import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, inputs
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, crossdomain, RESPONSE_OK
from ...models import db, status
from ...models.terminationform import Terminationform, TerminationformResponseModel
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP, LOG


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)

parser.add_argument('MemberName', type=str, location='json', required=True)
parser.add_argument('MemberNumber', type=str, location='json', required=True)
parser.add_argument('EmailAddress', type=str, location='json', required=True)
# parser.add_argument('FinalDateOfEmployment', type=inputs.date_from_iso8601, location='json', required=True)
# parser.add_argument('ReasonforTermination', type=str, location='json', required=True)
# parser.add_argument('LastDeduction', type=str, location='json', required=True)
# parser.add_argument('Address', type=str, location='json', required=True)
# parser.add_argument('AddressLine2', type=str, location='json', required=True)
# parser.add_argument('District', type=str, location='json', required=True)
# parser.add_argument('PostalCode', type=str, location='json', required=True)
# parser.add_argument('Country', type=str, location='json', required=True)
# parser.add_argument('EstimatedAnnualIncomeRange', type=str, location='json', required=True)
# parser.add_argument('Status', type=str, location='json', required=True)
parser.add_argument('Comment', type=str, location='json', required=False)


@ns.route("/initiate")
class TerminationInitiationController(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Initiate Termination',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(TerminationformResponseModel)
    def post(self):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] != ROLES_EMPLOYER:
            raise Unauthorized()

        employer_username = auth['username']
        initiation_date = datetime.utcnow()
        data = json.loads(str(request.data, encoding='utf-8'))
        employer_id = data["employernumber"]
        employer_name = data["employername"]
        # member_name = data["memberfirstName"]
        # form_type = data["formType"]
        # employer_comments = data["comments"]
        employernumber = employer_id
        member_name = args['MemberNumber']

        # data["formCreatedDate"] = datetime.utcnow()
        if str(employer_id)[-2:].__contains__("HR"):
            employernumber = str(employer_id)[:-2]

        form = Terminationform(
            EmployerName=employer_name,
            EmployerID=employer_username,
            InitiatedDate=initiation_date,
            MemberName=args['MemberName'],
            MemberNumber=args['MemberNumber'],
            EmailAddress=args['EmailAddress'],
            # FinalDateOfEmployment=args['FinalDateOfEmployment'],
            # ReasonforTermination=args['ReasonforTermination'],
            # LastDeduction=args['LastDeduction'],
            # Address=args['Address'],
            # AddressLine2=args['AddressLine2'],
            # District=args['District'],
            # PostalCode=args['PostalCode'],
            # Country=args['Country'],
            # EstimatedAnnualIncomeRange=args['EstimatedAnnualIncomeRange'],
            # Status=args['Status'],
            # PendingFrom=args['PendingFrom'],
        )

        db.session.add(form)
        db.session.commit()

        token = Token(
            FormID=form.FormID,
            EmployerID=employer_username,
            InitiatedBy=employer_username,
            InitiatedDate=initiation_date,
            FormStatus=status.STATUS_PENDING,
            FormType=TOKEN_FORMTYPE_TERMINATION,
            PendingFrom='Member',
            TokenStatus=status.STATUS_ACTIVE,
            LastModifiedDate=datetime.utcnow(),
        )

        db.session.add(token)
        db.session.commit()
        token_id = token.TokenID
        if 'Comment' in args and args['Comment'] != '':
            comment = Comments(
                FormID=form.FormID,
                Role=auth['role'],
                Comment=args['Comment'],
                Date=initiation_date,
            )
            db.session.add(comment)
            db.session.commit()

        try:
            subject = 'Please complete your Silver Thatch Pensions Employment Termination Form'
            # send_email(to_address=form.EmailAddress, subject=subject, template='termination_initiation_to_member.html')
            msgtext = MIMEText(
                '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>'
                '<p>Dear %s</p>'
                '<p>In an effort to keep you connected with your Silver Thatch Pension after you leave your '
                'current position, please click here or copy the link below into a browser to complete the '
                'termination of employment form. This form notifies us that you are no longer employed with '
                'your current employer and allows Silver Thatch Pensions to stay in touch with you in regards '
                'to your pension. </p><p>-----------------------------------------</p> '
                '<p>https://183.82.0.186:812/terminationform/%s</p>'
                '<p>To learn more about the Silver Thatch Pension Plan,'
                ' click here to review our members handbook. </p>' % (member_name, token_id), 'html')
            send_email(to_address=form.EmailAddress, subject=subject, body=msgtext)
            return RESPONSE_OK
        except Exception as e:
            LOG.warning('Unexpected error happened during initiating termination: %s', e)
            raise InternalServerError
