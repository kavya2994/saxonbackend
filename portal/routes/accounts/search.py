import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from sqlalchemy import or_

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, converter
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.member_view import MemberView
from ...models.employer_view import EmployerView
from ...models.users import Users
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('ID', type=str, location='json', required=False)
parser.add_argument('name', type=str, location='json', required=False)
parser.add_argument('user', type=str, location='json', required=False)
parser.add_argument('employerusername', type=str, location='json', required=False)
parser.add_argument('status', type=str, location='json', required=False)
parser.add_argument('email', type=str, location='json', required=False)
parser.add_argument('key', type=str, location='json', required=False)
parser.add_argument('role', type=str, location='json', required=False)
parser.add_argument('offset', type=int, location='json', required=True)

response_model_members = ns.model('GetSearchMembers', {
    'MKEY': fields.String,
    'MEMNO': fields.String,
    'FNAME': fields.String,
    'LNAME': fields.String,
    'EMAIL': fields.String,
    'PSTATUS': fields.String,
    'EM_STATUS': fields.String,

})

response_model_employers = ns.model('GetSearchEmployers', {
    'ERKEY': fields.String,
    'ERNO': fields.String,
    'ENAME': fields.String,
    'SNAME': fields.String,
    'EMAIL': fields.String,
})

response_model = ns.model('GetSearch', {
    'members': fields.List(fields.Nested(response_model_members)),
    'employers': fields.List(fields.Nested(response_model_employers)),
})


@ns.route("/search")
class Search(Resource):
    @ns.doc(description='search functionality',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        offset_ = args["offset"]
        if decoded_token["role"] not in [roles.ROLES_ADMIN, roles.ROLES_REVIEW_MANAGER, roles.ROLES_EMPLOYER]:
            raise Unauthorized()
        args_list = ["ID", "name", "user", "status", "email", "key", "employerusername"]
        args_dict = {}
        for arg in args_list:
            if args[arg] is None:
                args_dict[arg] = ""
            else:
                args_dict[arg] = args[arg]

        search_role = args["role"]

        if search_role == roles.ROLES_MEMBER:
            employer_username = args_dict["employerusername"]
            employer_sname = ""
            if not employer_username == "":
                employer_ = EmployerView.query.filter_by(ERNO=employer_username).first()
                if employer_ is not None:
                    employer_sname = employer_.SNAME
            try:
                members = MemberView.query.filter(MemberView.MEMNO.like("%" + args_dict["ID"] + "%"),
                                                  or_(MemberView.FNAME.like("%" + args_dict["name"] + "%"),
                                                      MemberView.LNAME.like("%" + args_dict["name"] + "%")),
                                                  MemberView.EMAIL.like("%" + args_dict["email"] + "%"),
                                                  MemberView.PSTATUS.like("%" + args_dict["status"] + "%"),
                                                  MemberView.EMPOYER.like("%" + employer_sname + "%")) \
                    .offset(offset_).limit(25).all()
                if members is not None:
                    member_list = []
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
                    # print(member_list)
                    return json.dumps({"members": member_list}, default=converter)
                else:
                    return {"members": []}
            except Exception as e:
                LOG.error(e)
                raise InternalServerError("Can't retrieve members")
        elif search_role == roles.ROLES_EMPLOYER:
            try:
                employers = EmployerView.query.filter(EmployerView.EMAIL.like("%" + args_dict["email"] + "%"),
                                                      EmployerView.ERKEY.like("%" + args_dict["key"] + "%"),
                                                      EmployerView.ERNO.like("%" + args_dict["employerusername"] + "%"),
                                                      EmployerView.ENAME.like("%" + args_dict["name"] + "%")
                                                      ).offset(offset_).limit(25).all()
                employer_list = []
                if employers is not None:
                    for emp in employers:
                        employer_list.append({
                            'ERKEY': emp.ERKEY,
                            'ERNO': emp.ERNO,
                            'ENAME': emp.ENAME,
                            'SNAME': emp.SNAME,
                            'EMAIL': emp.EMAIL
                        })
                    return {"employers": employer_list}, 200
                else:
                    return {"employers": []}, 200
            except Exception as e:
                LOG.error(e)
                raise InternalServerError("Can't retrieve employers")
        else:
            raise UnprocessableEntity()
