import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models import db, status, roles
from ...models.terminationform import Terminationform
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
parser.add_argument('Comment', type=str, location='json', required=False)
parser.add_argument('CommentName', type=str, location='json', required=False)

response_model = ns.model('PostTerminationInitiationController', {
    'FormID': fields.String,
    'EmployerName': fields.String,
    'InitiatedDate': fields.DateTime,
    'MemberName': fields.String,
    'MemberNumber': fields.String,
    'EmailAddress': fields.String,
    'FinalDateOfEmployment': fields.Date,
    'ReasonforTermination': fields.Date,
    'LastDeduction': fields.String,
    'Address': fields.String,
    'AddressLine2': fields.String,
    'District': fields.String,
    'PostalCode': fields.String,
    'Country': fields.String,
    'EstimatedAnnualIncomeRange': fields.String,
    'Status': fields.String,
    'EmployerID': fields.String,
    'PendingFrom': fields.String,
})


@ns.route("/initiate")
class TerminationInitiationController(Resource):
    @ns.doc(description='Initiate Termination',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] == ROLES_MEMBER or auth['role'] == '':
            raise Unauthorized()

        intiated_by = auth['username']
        initiation_date = datetime.utcnow()
        data = json.loads(str(request.data, encoding='utf-8'))
        print(data)
        employer_id = data["employerusername"]
        employer_name = data["employername"]
        employernumber = employer_id
        member_name = args['MemberNumber']

        # data["formCreatedDate"] = datetime.utcnow()
        if str(employer_id)[-2:].__contains__("HR"):
            employernumber = str(employer_id)[:-2]

        form = Terminationform(
            EmployerName=employer_name,
            EmployerID=employer_id,
            InitiatedDate=initiation_date,
            MemberName=args['MemberName'],
            MemberNumber=args['MemberNumber'],
            EmailAddress=args['EmailAddress'],
            Status=status.STATUS_PENDING,
            PendingFrom=roles.ROLES_MEMBER

        )

        db.session.add(form)
        db.session.commit()

        token = Token(
            FormID=form.FormID,
            EmployerID=employer_id,
            InitiatedBy=intiated_by,
            InitiatedDate=initiation_date,
            FormStatus=status.STATUS_PENDING,
            FormType=TOKEN_FORMTYPE_TERMINATION,
            PendingFrom=roles.ROLES_MEMBER,
            TokenStatus=status.STATUS_ACTIVE,
            LastModifiedDate=datetime.utcnow(),
        )

        db.session.add(token)
        db.session.commit()
        token_id = token.TokenID
        if 'Comment' in args and args['Comment'] != '':
            comment = Comments(
                FormID=form.FormID,
                Name=employer_name,
                Role=auth['role'],
                Comment=args['Comment'],
                Date=initiation_date,
            )
            db.session.add(comment)
            db.session.commit()

        try:
            subject = 'Please complete your Silver Thatch Pensions Employment Termination Form'
            msg_text = \
                f'<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>' + \
                f'<p>Dear {member_name}</p>' + \
                f'<p>In an effort to keep you connected with your Silver Thatch Pension after you leave your ' + \
                f'current position, please click here or copy the link below into a browser to complete the ' + \
                f'termination of employment form. This form notifies us that you are no longer employed with ' + \
                f'your current employer and allows Silver Thatch Pensions to stay in touch with you in regards ' + \
                f'to your pension. </p><p>-----------------------------------------</p> ' + \
                f'<p>{APP.config["FRONTEND_URL"]}/terminationform/{token_id}</p>' + \
                f'<p>To learn more about the Silver Thatch Pension Plan,' + \
                f' click here to review our members handbook. </p>'

            send_email(to_address=form.EmailAddress, subject=subject, body=msg_text)
            return RESPONSE_OK
        except Exception as e:
            LOG.warning('Unexpected error happened during initiating termination: %s', e)
            raise InternalServerError
