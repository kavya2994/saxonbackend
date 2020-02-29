import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
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
parser.add_argument('offset', type=str, location='args', required=False)


response_model_child = ns.model('GetGetMembersChild', {
    'MKEY': fields.String,
    'MEMNO': fields.String,
    'FNAME': fields.String,
    'LNAME': fields.String,
    'EMAIL': fields.String,
    'PSTATUS': fields.String,
    'EM_STATUS': fields.String
})

response_model = ns.model('GetGetMembers', {
    "members": fields.List(fields.Nested(response_model_child))
})


@ns.route("/members/get")
class GetMembers(Resource):
    @ns.doc(description='Get all members in b/w min and max',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        offset = args["offset"]
        decoded_token = token_verify_or_raise(token, username, ip)
        member_list = []

        if offset is None or str(offset) == "":
            offset = 0

        if decoded_token["role"] not in [roles.ROLES_ADMIN, roles.ROLES_REVIEW_MANAGER]:
            raise Unauthorized()

        LOG.info('GetMembers: fetching MemberView, offset: %s, limit: 50', offset)
        members = MemberView.query.offset(offset).limit(50).all()
        LOG.info('GetMembers: finished fetching MemberView. Got %s result', len(members))

        if members is not None:
            for mem in members:
                member_list.append({
                    'MKEY': mem.MKEY,
                    'MEMNO': mem.MEMNO,
                    'FNAME': mem.FNAME,
                    'LNAME': mem.LNAME,
                    'EMAIL': mem.EMAIL,
                    'PSTATUS': mem.PSTATUS,
                    'EM_STATUS': mem.EM_STATUS
                })

        return {"members": member_list}


