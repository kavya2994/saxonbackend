import json
import os
import threading
from datetime import datetime
import time

import xlrd
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK, delete_excel
from ...models import db, status, roles
from ...models.member_view import MemberView
from ...models.employer_view import EmployerView
from xlutils.copy import copy
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('employerusername', type=str, location='json', required=True)
parser.add_argument('employername', type=str, location='json', required=True)


@ns.route("/build/excel")
class BuildExcel(Resource):
    @ns.doc(description='Generates and Excel sheet of members under employer',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            return Unauthorized()
        employer_username = args["employerusername"]
        employer_name = args["employername"]
        template_path = os.path.join(APP.config['EXCEL_TEMPLATE_DIR'], 'Contributionex.xls')

        current_datetime = datetime.utcnow()
        rb = xlrd.open_workbook(template_path, formatting_info=True)

        wb = copy(rb)

        w_sheet = wb.get_sheet(0)

        w_sheet.write(9, 1, employer_name)
        w_sheet.write(9, 5, employer_username)

        # empuser = db1.collection("members").where("employers", "array_contains",
        #                                           db1.collection("employers").document(employer_username)).stream()
        employer_data = EmployerView.query.filter_by(ERNO=employer_username).first()
        if employer_data is None:
            raise UnprocessableEntity("Can't find employer", employer_username)
        member_data = MemberView.query.filter(MemberView.EMPOYER == employer_data.SNAME,
                                              MemberView.EM_STATUS != "Terminated").all()
        i = 16
        for doc in member_data:
            w_sheet.write(i, 0, doc.MEMNO)
            w_sheet.write(i, 1, doc.LNAME)
            w_sheet.write(i, 2, doc.FNAME)
            i += 1
        filename = os.path.join(APP.config['EXCEL_TEMPLATE_DIR'],
                                current_datetime.strftime("%d%m%Y %H%M%S") + 'Contribution.xls')

        wb.save(filename)
        t = threading.Thread(target=delete_excel, args=(filename,))
        t.start()
        return send_file(filename)
