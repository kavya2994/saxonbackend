import base64
import os
import threading
import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app, send_file
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, delete_excel
from ...encryption import Encryption
from ...models import db, status
from ...models.roles import *
from ...models.member_view import MemberView
from ...models.employer_dealing_day_rpt import EmployerDealingDayRPT
from ...models.employer_view import EmployerView
from ...models.beneficiary_read import BeneficiaryFromRead
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('user', type=str, location='args', required=True)

response_model = ns.model('GetReports', {
    "DateFrom": fields.String,
    "DateTo": fields.String,
    "FileName": fields.String
})

response = ns.model("GetReportsList", {
    "Files": fields.List(fields.Nested(response_model))
})


@ns.route("/employerreports/get")
class GetStatements(Resource):
    @ns.doc(description='Get Employer reports',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        user = args['user']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token['role'] not in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        employer = EmployerView.query.filter_by(ERNO=user).first()
        if employer is None:
            raise UnprocessableEntity("Not a valid employer")
        statements = []
        employer_reports = EmployerDealingDayRPT.query.filter_by(ERKEY=employer.ERKEY).all()
        for statement in employer_reports:
            statements.append({
                "DateFrom": statement.DATE_FROM,
                "DateTo": statement.DATE_TO,
                "FileName": statement.FILENAME
            })

        return {"Files": statements}, 200


@ns.route("/employerreport/get/<FileName>")
class GetStatements(Resource):
    @ns.doc(description='Get employer report file pdf',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def get(self, FileName):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        user = args['user']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token['role'] not in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        employer = EmployerView.query.filter_by(ERNO=user).first()
        if employer is None:
            raise UnprocessableEntity("Not a valid employer")
        employer_report = EmployerDealingDayRPT.query.filter_by(FILENAME=FileName, ERKEY=employer.ERKEY).first()
        if employer_report is None:
            raise UnprocessableEntity("Not a valid file")
        filepath = os.path.join(APP.config["EXCEL_TEMPLATE_DIR"], FileName)
        file = open(filepath, 'wb')
        file.write(employer_report.FILEITEM)
        file.close()
        t = threading.Thread(target=delete_excel, args=(filepath,))
        t.start()
        return send_file(filepath)
