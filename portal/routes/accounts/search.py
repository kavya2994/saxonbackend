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
    'MEMNO': fields.String,
    'FNAME': fields.String,
    'LNAME': fields.String,
    'EMAIL': fields.String,
    'PSTATUS': fields.String,
    'EM_STATUS': fields.String,

})

response_model_employers = ns.model('GetSearchEmployers', {
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
        if decoded_token["role"] not in [roles.ROLES_ADMIN, roles.ROLES_REVIEW_MANAGER, roles.ROLES_EMPLOYER,
                                         roles.ROLES_HR]:
            raise Unauthorized()
        args_list = ["ID", "name", "user", "status", "email", "employerusername"]
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
            if not (employer_username == "" and employer_username is not None):
                employer_ = EmployerView.query.filter_by(ERNO=employer_username).first()
                if employer_ is None:
                    return {"members": []}
                employer_sname = employer_.SNAME
            try:
                members = None
                if args_dict["email"] != "" and args_dict["email"] is not None:
                    members = MemberView.query.filter(MemberView.MEMNO.ilike("%" + args_dict["ID"] + "%"),
                                                      or_(MemberView.FNAME.ilike("%" + args_dict["name"] + "%"),
                                                          MemberView.LNAME.ilike("%" + args_dict["name"] + "%")),
                                                      MemberView.EMAIL.ilike("%" + args_dict["email"] + "%"),
                                                      MemberView.PSTATUS.ilike("%" + args_dict["status"] + "%"),
                                                      MemberView.EMPOYER.ilike("%" + employer_sname + "%"),
                                                      MemberView.EM_STATUS != "Terminated") \
                        .offset(offset_).limit(50).all()
                else:
                    members = MemberView.query.filter(MemberView.MEMNO.ilike("%" + args_dict["ID"] + "%"),
                                                      or_(MemberView.FNAME.ilike("%" + args_dict["name"] + "%"),
                                                          MemberView.LNAME.ilike("%" + args_dict["name"] + "%")),
                                                      # MemberView.EMAIL.ilike("%" + args_dict["email"] + "%"),
                                                      MemberView.PSTATUS.ilike("%" + args_dict["status"] + "%"),
                                                      MemberView.EMPOYER.ilike("%" + employer_sname + "%"),
                                                      MemberView.EM_STATUS != "Terminated") \
                        .offset(offset_).limit(50).all()
                if members is None:
                    return {"members": []}
                member_list = []
                for mem in members:
                    member_list.append({
                        'MEMNO': mem.MEMNO,
                        'FNAME': mem.FNAME,
                        'LNAME': mem.LNAME,
                        'EMAIL': mem.EMAIL,
                        'PSTATUS': mem.PSTATUS,
                        'EM_STATUS': mem.EM_STATUS
                    })

                return {"members": member_list}

            except Exception as e:
                LOG.error(e)
                raise InternalServerError("Can't retrieve members")
        elif search_role == roles.ROLES_EMPLOYER:
            try:
                employers = None
                if args_dict["email"] != "" and args_dict["email"] is not None:
                    employers = EmployerView.query.filter(EmployerView.EMAIL.ilike("%" + args_dict["email"] + "%"),
                                                          EmployerView.ERNO.ilike(
                                                              "%" + args_dict["employerusername"] + "%"),
                                                          EmployerView.ENAME.ilike("%" + args_dict["name"] + "%")
                                                          ).offset(offset_).limit(50).all()
                else:
                    employers = EmployerView.query.filter(EmployerView.ERNO.ilike(
                        "%" + args_dict["employerusername"] + "%"),
                        EmployerView.ENAME.ilike("%" + args_dict["name"] + "%")
                    ).offset(offset_).limit(50).all()
                employer_list = []
                if employers is None:
                    return {"employers": []}, 200
                for emp in employers:
                    employer_list.append({
                        'ERNO': emp.ERNO,
                        'ENAME': emp.ENAME,
                        'SNAME': emp.SNAME,
                        'EMAIL': emp.EMAIL
                    })
                return {"employers": employer_list}, 200
            except Exception as e:
                LOG.error(e)
                raise InternalServerError("Can't retrieve employers")
        else:
            raise UnprocessableEntity()
