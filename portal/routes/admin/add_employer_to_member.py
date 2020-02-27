import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.emp_mem_relation import EmpMemRelation
from ...models.employer_member_relation import EmpMemRel
from ...models.employer import Employer
from ...models.member import Member
from ...services.mail import send_email
from ...models.security_question import SecurityQuestion
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('employer_id', type=str, location='json', required=True)
parser.add_argument('member_id', type=str, location='json', required=True)
parser.add_argument('member_name', type=str, location='json', required=True)
parser.add_argument('employer_name', type=str, location='json', required=True)

response_model = ns.model('PostAddEmployerMemberRelation', {
    "result": fields.String,
})

@ns.route("/addemployertomember")
class AddEmployerMemberRelation(Resource):
    @ns.doc(parser=parser,
            description='Add employer to a member',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
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

            emp_mem = EmpMemRelation(
                EmployerID=employer_id,
                EmployerName=employer_name,
                MemberID=member_id,
                MemberName=member_name
            )

            # relation = EmpMemRel(
            # EmployerID=employer_id,
            #     EmployerName=employer_name,
            #     MemberID=member_id,
            #     MemberName=member_name
            # )
            try:
                db.session.add(emp_mem)
                db.session.commit()
                return {"result": "Success"}, 200
            except Exception as e:
                LOG.error("Exception while adding employer to member", e)
                raise InternalServerError("Can't add employer to user")
        else:
            Unauthorized()
