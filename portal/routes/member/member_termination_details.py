import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)

parser.add_argument('memberid', type=str, location='json', required=True)


@ns.route("/member/terminationdetails")
class MemberTerminationDetails(Resource):
    @ns.doc(parser=parser,
            description='Get member termination details ',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 422: 'UnprocessableEntity',
                       500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def get(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        # TODO:
        # Verify the role from token before proceeding with password chanaging

        username = args["Username"]

