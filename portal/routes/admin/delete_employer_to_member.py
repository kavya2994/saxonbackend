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

response_model = ns.model('PostDeleteEmployerMemberRelation', {
    "result": fields.String,
})

@ns.route("/delemployertomember")
class DeleteEmployerMemberRelation(Resource):
    @ns.doc(description='delete employer member relation',
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
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_ADMIN:
            try:
                EmpMemRelation.query.filter(EmpMemRelation.EmployerID == employer_id,
                                            EmpMemRelation.MemberID == member_id).delete()
                db.session.commit()
                return {"result": "Success"}, 200
            except Exception as e:
                LOG.error('Exception while deleting memberid %s employerid %s %s' % (
                    args["member_id"], args["employer_id"], e))
                raise InternalServerError()
        else:
            raise Unauthorized()
