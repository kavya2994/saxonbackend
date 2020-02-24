import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.member_view import MemberView
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('membernumber', type=str, location='args', required=True)

response_model = {
    'MKEY': fields.String,
    'MEMNO': fields.String,
    'FNAME': fields.String,
    'LNAME': fields.String,
    'EMAIL': fields.String,
    'BIRTH': fields.String,
    'ENTRY_DATE': fields.String,
    'NR_DATE': fields.String,
    'HIRE': fields.String,
    'PSTATUS': fields.String,
    'EMPOYER': fields.String,
    'STREET1': fields.String,
    'EM_STATUS': fields.String,
    'CITY': fields.String,
    'COUNTRY': fields.String,
    'BEN_NAMES': fields.String,
    'RELNAME': fields.String,
    'ER_DATE': fields.String
}


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/data/get")
class GetMemberDetails(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get profile details',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        user = args["membernumber"]
        print(user)
        decoded_token = token_verify_or_raise(token, username, ip)
        member = MemberView.query.filter_by(MEMNO=user).first()
        if member is not None:
            return {
                       'MKEY': member.MKEY,
                       'MEMNO': member.MEMNO,
                       'FNAME': member.FNAME,
                       'LNAME': member.LNAME,
                       'EMAIL': member.EMAIL,
                       'BIRTH': member.BIRTH,
                       'ENTRY_DATE': member.ENTRY_DATE,
                       'NR_DATE': member.NR_DATE,
                       'HIRE': member.HIRE,
                       'PSTATUS': member.PSTATUS,
                       'EMPOYER': member.EMPOYER,
                       'STREET1': member.STREET1,
                       'EM_STATUS': member.EM_STATUS,
                       'CITY': member.CITY,
                       'COUNTRY': member.COUNTRY,
                       'BEN_NAMES': member.BEN_NAMES,
                       'RELNAME': member.RELNAME,
                       'ER_DATE': member.NR_DATE.replace(year=member.NR_DATE.year - 10)
                   }, 200
        else:
            LOG.debug("Can't find member details", user)
            raise UnprocessableEntity("Can't find member")
