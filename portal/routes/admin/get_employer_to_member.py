import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.emp_mem_relation import EmpMemRelation
from ...models.employer_view import EmployerView
from ...models.member_view import MemberView
from ...models.employer_member_relation import EmpMemRel
from werkzeug.exceptions import UnprocessableEntity, Unauthorized
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('member_id', type=str, location='args', required=True)

response_model = {
    "EmployerNo": fields.String,
    "EmployerName": fields.String
}

response = {
    "employers": fields.List(fields.Nested(response_model))
}


@ns.route("/getemployertomember")
class GetEmployerMemberRelation(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='get employer to a member',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        member_id = args["member_id"]
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_ADMIN:
            employers_data_list = []
            employers_list = []
            employers_from_view = db.session.query(MemberView, EmployerView).filter(
                MemberView.EMPOYER == EmployerView.SNAME,
                MemberView.MEMNO == member_id).all()
            if employers_from_view is not None:
                for employers in employers_from_view:
                    employers_data_list.append({
                        "EmployerNo": employers.ERNO,
                        "EmployerName": employers.ENAME
                    })
                    employers_list.append(employers.ERNO)

            employers_from_writedb = EmpMemRelation.query.filter_by(MemberID=member_id).all()
            if employers_from_writedb is not None:
                for employers in employers_from_writedb:
                    if employers.EmployerID not in employers_list:
                        employers_data_list.append({
                            "EmployerNo": employers.EmployerID,
                            "EmployerName": employers.EmployerName
                        })
            return {"employers": employers_data_list}, 200

        else:
            return Unauthorized()
