import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, inputs
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, crossdomain, RESPONSE_OK
from ...models import db, status, roles
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
parser.add_argument('Comment', type=str, location='json', required=False)
parser.add_argument('CommentName', type=str, location='json', required=False)


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
            EmployerID=employernumber,
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
            EmployerID=employernumber,
            InitiatedBy=employer_id,
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
            msg_text = MIMEText(
                '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>'
                '<p>Dear %s</p>'
                '<p>In an effort to keep you connected with your Silver Thatch Pension after you leave your '
                'current position, please click here or copy the link below into a browser to complete the '
                'termination of employment form. This form notifies us that you are no longer employed with '
                'your current employer and allows Silver Thatch Pensions to stay in touch with you in regards '
                'to your pension. </p><p>-----------------------------------------</p> '
                '<p>%s/terminationform/%s</p>'
                '<p>To learn more about the Silver Thatch Pension Plan,'
                ' click here to review our members handbook. </p>' % (member_name, APP.config["FRONTEND_URL"], token_id), 'html')
            send_email(to_address=form.EmailAddress, subject=subject, body=msg_text)
            return RESPONSE_OK
        except Exception as e:
            LOG.warning('Unexpected error happened during initiating termination: %s', e)
            raise InternalServerError
