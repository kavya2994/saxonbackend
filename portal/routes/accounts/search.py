import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from sqlalchemy import or_

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
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


@ns.route("/search")
class Search(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='search functionality',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)

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
                members = MemberView.query.filter(MemberView.MKEY.like("%" + args_dict["ID"] + "%"),
                                                  or_(MemberView.FNAME.like("%" + args_dict["name"] + "%"),
                                                      MemberView.LNAME.like("%" + args_dict["name"] + "%")),
                                                  MemberView.EMAIL.like("%" + args_dict["email"] + "%"),
                                                  MemberView.PSTATUS.like("%" + args_dict["status"] + "%"),
                                                  MemberView.EMPOYER.like("%" + employer_sname + "%")).all()
                if members is not None:
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

                    return {"members": member_list}, 200
                else:
                    return {}, 200
            except Exception as e:
                LOG.error(e)
                raise InternalServerError("Can't retrieve members")
        elif search_role == roles.ROLES_EMPLOYER:
            try:
                employers = EmployerView.query.filter(EmployerView.EMAIL.like("%" + args_dict["email"] + "%"),
                                                      EmployerView.ERKEY.like("%" + args_dict["key"] + "%"),
                                                      EmployerView.ERNO.like("%" + args_dict["employerusername"] + "%"),
                                                      EmployerView.ENAME.like("%" + args_dict["name"] + "%")
                                                      ).all()
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



