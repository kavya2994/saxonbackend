import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from sqlalchemy import or_

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.employer_view import EmployerView
from ...models.member_view import MemberView
from ...models.emp_mem_relation import EmpMemRelation
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('offset', type=int, location='args', required=True)

response_model_child = ns.model('GetGetMembersChild', {
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


@ns.route("/members/get/<EmployerID>")
class GetMembersForEmployer(Resource):
    @ns.doc(description='Get all members in b/w min and max',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self, EmployerID):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        offset = args["offset"]
        decoded_token = token_verify_or_raise(token, username, ip)

        if decoded_token["role"] not in [roles.ROLES_EMPLOYER, roles.ROLES_HR, roles.ROLES_REVIEW_MANAGER]:
            raise Unauthorized()

        if EmployerID is None:
            raise UnprocessableEntity("Not a valid employerid")
        employer_ = EmployerView.query.filter_by(ERNO=EmployerID).first()
        if employer_ is None:
            raise UnprocessableEntity("Not a valid employerid")
        try:
            member_list_write_db = []
            members_from_db = EmpMemRelation.query.filter(EmpMemRelation.EmployerID == EmployerID).all()
            if members_from_db is not None:
                for members_ in members_from_db:
                    # if members_.MemberID not in member_list_read_db:
                    member_list_write_db.append(members_.MemberID)
            employer_sname = employer_.SNAME
            members = MemberView.query.filter(or_(MemberView.EMPOYER == employer_sname,
                                                  MemberView.MEMNO.in_(tuple(member_list_write_db))),
                                              MemberView.EM_STATUS.ilike("%FULL%"),
                                              MemberView.PSTATUS.ilike("%active%")).order_by(MemberView.MEMNO.desc()) \
                .offset(offset).limit(50).all()
            member_list = []
            # member_list_read_db = []
            for mem in members:
                member_list.append({
                    'MEMNO': mem.MEMNO,
                    'FNAME': mem.FNAME,
                    'LNAME': mem.LNAME,
                    'EMAIL': mem.EMAIL,
                    'PSTATUS': mem.PSTATUS,
                    'EM_STATUS': mem.EM_STATUS
                })
                # member_list_read_db.append(mem.MEMNO)

            # members_fetch_from_write = MemberView.query.filter(MemberView.MEMNO.in_(tuple(member_list_write_db)),
            #                                                    MemberView.EM_STATUS != "Terminated") \
            #     .all()
            # if members_fetch_from_write is not None:
            #     for mem in members_fetch_from_write:
            #         member_list.append({
            #             'MEMNO': mem.MEMNO,
            #             'FNAME': mem.FNAME,
            #             'LNAME': mem.LNAME,
            #             'EMAIL': mem.EMAIL,
            #             'PSTATUS': mem.PSTATUS,
            #             'EM_STATUS': mem.EM_STATUS
            #         })

            return {"members": member_list}, 200
        except Exception as e:
            LOG.error("cant get members", e)
            raise InternalServerError("Can't get members")
