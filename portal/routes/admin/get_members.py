import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.member_view import MemberView
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('min', type=str, location='json', required=True)
parser.add_argument('max', type=str, location='json', required=True)

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
    'RELNAME': fields.String
}


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/members/get")
class GetMembers(Resource):
    @ns.doc(parser=parser,
            description='Get all members in b/w min and max',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['Username']
        token = args["Authorization"]
        ip = args['IpAddress']
        minimum = args["min"]
        maximum = args["max"]
        decoded_token = token_verify_or_raise(token, username, ip)

        if decoded_token["role"] == roles.ROLES_ADMIN:
            members = MemberView.query.limit(minimum).offset(maximum)
            member_list = []
            for mem in members:
                member_list.append({
                    'MKEY': mem.MKEY,
                    'MEMNO': mem.MEMNO,
                    'FNAME': mem.FNAME,
                    'LNAME': mem.LNAME,
                    'EMAIL': mem.EMAIL,
                    'BIRTH': mem.BIRTH,
                    'ENTRY_DATE': mem.ENTRY_DATE,
                    'NR_DATE': mem.NR_DATE,
                    'HIRE': mem.HIRE,
                    'PSTATUS': mem.PSTATUS,
                    'EMPOYER': mem.EMPOYER,
                    'STREET1': mem.STREET1,
                    'EM_STATUS': mem.EM_STATUS,
                    'CITY': mem.CITY,
                    'COUNTRY': mem.COUNTRY,
                    'BEN_NAMES': mem.BEN_NAMES,
                    'RELNAME': mem.RELNAME
                })
            return {"employers": member_list}, 200
        else:
            raise Unauthorized()
