import os
import threading
from threading import Thread

import jwt
import json
from datetime import datetime

import xlrd
import xlsxwriter
from flask import Blueprint, jsonify, request, abort, current_app as app, send_file
from flask_restx import Resource, reqparse, fields
from sqlalchemy import or_

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, delete_excel
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.employer_view import EmployerView
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG
from ...models.member_view import MemberView

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


@ns.route("/export")
class ExportAccounts(Resource):
    @ns.doc(description='Get all employers in b/w min and max',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    # @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] not in [roles.ROLES_ADMIN, roles.ROLES_REVIEW_MANAGER, roles.ROLES_EMPLOYER,
                                         roles.ROLES_HR]:
            raise Unauthorized()
        args_list = ["ID", "name", "user", "status", "email", "key", "employerusername"]
        args_dict = {}
        for arg in args_list:
            if args[arg] is None:
                args_dict[arg] = ""
            else:
                args_dict[arg] = args[arg]

        search_role = args["role"]
        accounts_list = []
        if search_role == roles.ROLES_MEMBER:
            employer_username = args_dict["employerusername"]
            employer_sname = ""
            if not employer_username == "" and employer_username is not None:
                employer_ = EmployerView.query.filter_by(ERNO=employer_username).first()
                if employer_ is None:
                    raise UnprocessableEntity("Invalid employer")
                employer_sname = employer_.SNAME
            try:
                members = MemberView.query.filter(MemberView.MEMNO.ilike("%" + args_dict["ID"] + "%"),
                                                  or_(MemberView.FNAME.ilike("%" + args_dict["name"] + "%"),
                                                      MemberView.LNAME.ilike("%" + args_dict["name"] + "%")),
                                                  MemberView.EMAIL.ilike("%" + args_dict["email"] + "%"),
                                                  MemberView.PSTATUS.ilike("%" + args_dict["status"] + "%"),
                                                  MemberView.EMPOYER.ilike("%" + employer_sname + "%"),
                                                  MemberView.EM_STATUS != "Terminated").all()
                if members is not None:
                    for mem in members:
                        accounts_list.append({
                            # 'Number': mem.MEMNO,
                            # 'Name': mem.FNAME if mem.FNAME is not None else "" + " " + mem.LNAME if mem.LNAME is not None else "",
                            # 'Email': mem.EMAIL
                            'MEMNO': mem.MEMNO,
                            'FNAME': mem.FNAME,
                            'LNAME': mem.LNAME,
                            'EMAIL': mem.EMAIL,
                            'PSTATUS': mem.PSTATUS,
                            'EM_STATUS': mem.EM_STATUS,
                            'BIRTH': mem.BIRTH,
                            'ENTRY_DATE': mem.ENTRY_DATE,
                            'NR_DATE': mem.NR_DATE,
                            'HIRE': mem.HIRE,
                            'EMPOYER': mem.EMPOYER,
                            'STREET1': mem.STREET1,
                            'STREET2': mem.STREET2,
                            'CITY': mem.CITY,
                            'POSTAL': mem.POSTAL,
                            'COUNTRY': mem.COUNTRY,
                            'BEN_NAMES': mem.BEN_NAMES,
                            'RELNAME': mem.RELNAME
                        })
                filepath = self.build_excel_accounts(accounts_list, search_role)
                t = threading.Thread(target=delete_excel, args=(filepath,))
                t.start()
                return send_file(filepath, attachment_filename=search_role + ".xlsx")
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
                                                          ).all()
                else:
                    employers = EmployerView.query.filter(EmployerView.ERNO.ilike(
                        "%" + args_dict["employerusername"] + "%"),
                        EmployerView.ENAME.ilike("%" + args_dict["name"] + "%")
                    ).all()
                if employers is not None:
                    for emp in employers:
                        accounts_list.append({
                            # 'Number': emp.ERNO,
                            # 'Name': emp.ENAME,
                            # 'Email': emp.EMAIL
                            'ERKEY': emp.ERKEY,
                            'ERNO': emp.ERNO,
                            'ENAME': emp.ENAME,
                            'SNAME': emp.SNAME,
                            'EMAIL': emp.EMAIL,
                            'ENTRY': emp.ENTRY,
                            'TERMDATE': emp.TERMDATE
                        })
                filepath = self.build_excel_accounts(accounts_list, search_role)
                t = threading.Thread(target=delete_excel, args=(filepath,))
                t.start()
                return send_file(filepath, attachment_filename=search_role + ".xlsx")
            except Exception as e:
                LOG.error(e)
                raise InternalServerError("Can't retrieve employers")
        else:
            raise UnprocessableEntity()

    def build_excel_accounts(self, accounts, account_type):
        filename = datetime.utcnow().strftime("%Y%m%d %H%M%S%f") + account_type + '.xls'
        file_path = os.path.join(APP.config['EXCEL_TEMPLATE_DIR'], filename)
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet(account_type)
        data_cell_format = workbook.add_format({
            'bold': 0,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        header_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        date_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'num_format': 'd mmmm yyyy'})

        # keys = accounts
        # worksheet.write(0, 0, "Number", header_format)
        # worksheet.write(0, 1, "Name", header_format)
        # worksheet.write(0, 2, "Email", header_format)
        i = 0

        for account in accounts:
            keys = list(account.keys())
            for key in keys:
                if i == 0:
                    worksheet.write(0, keys.index(key), key, header_format)
                    continue
                if isinstance(account[key], datetime.date):
                    worksheet.write(i, keys.index(key), account[key], date_format)
                    continue
                worksheet.write(i, keys.index(key), account[key], data_cell_format)
            i += 1
        workbook.close()
        return file_path
