import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.employer_member_relation import EmpMemRel
from ...services.mail import send_email
from ...models.security_question import SecurityQuestion
from werkzeug.exceptions import UnprocessableEntity, Unauthorized
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('employer_id', type=str, location='json', required=True)
parser.add_argument('member_id', type=str, location='json', required=True)
parser.add_argument('member_name', type=str, location='json', required=True)
parser.add_argument('employer_name', type=str, location='json', required=True)


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/addemployertomember")
class AddEmployerMemberRelation(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Add employer to a member',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        employer_id = args["employer_id"]
        member_id = args["member_id"]
        member_name = args["member_name"]
        employer_name = args["employer_name"]
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_ADMIN:
            relation = EmpMemRel(
                EmployerID=employer_id,
                EmployerName=employer_name,
                MemberID=member_id,
                MemberName=member_name
                )
            EmpMemRel.add(relation)
            db.session.commit()
        else:
            Unauthorized()