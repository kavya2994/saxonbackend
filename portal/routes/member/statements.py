import base64

import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app, send_file
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status
from ...models.roles import *
from ...models.member_view import MemberView
from ...models.monthly_statements import MonthlyStatements
from ...models.annual_statement import AnnualStatements
from ...models.member_view import MemberView
from ...models.beneficiary_read import BeneficiaryFromRead
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('statementtype', type=str, location='args', required=True)
parser.add_argument('user', type=str, location='args', required=True)

response_model = ns.model('GetFiles', {
    "DateFrom": fields.String,
    "DateTo": fields.String,
    "FileName": fields.String,
    "File": fields.String
})

response = ns.model("GetFilesList", {
    "Files": fields.List(fields.Nested(response_model))
})


@ns.route("/statement/get")
class GetStatements(Resource):
    @ns.doc(description='Get Statements',
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
        if decoded_token['role'] not in [ROLES_MEMBER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        member = MemberView.query.filter_by(MEMNO=user).first()
        if member is None:
            raise UnprocessableEntity("Not a valid member")
        statements = []
        if args["statementtype"] == "Annual":
            annual_statements = AnnualStatements.query.filter_by(MKEY=member.MKEY).all()
            for statement in annual_statements:
                statements.append({
                    "DateFrom": statement.DATE_FROM,
                    "DateTo": statement.DATE_TO,
                    "FileName": statement.FILENAME,
                    "File": str(statement.FILEITEM).encode('utf-8')
                })
                LOG.info(statement.FILENAME, "Annual", member.MKEY)

        elif args["statementtype"] == "Monthly":
            monthly_statements = MonthlyStatements.query.filter_by(MKEY=member.MKEY).all()
            for statement in monthly_statements:
                statements.append({
                    "DateFrom": statement.DATE_FROM,
                    "DateTo": statement.DATE_TO,
                    "FileName": statement.FILENAME,
                    "File": str(statement.FILEITEM).encode('utf-8')
                })
                LOG.info(statement.FILENAME, "Monthly", member.MKEY)
        else:
            raise BadRequest("Not a valid request")
        return {"Files": statements}, 200


@ns.route("/statement/test/get")
class GetStatements(Resource):
    @ns.doc(description='Get Statements',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response)
    def get(self):
        monthly_statements = MonthlyStatements.query.filter_by(
            FILENAME="0001-286304-1-20190801-20190831.082910.PDF").first()
        with open('C:\\Users\\Manomay\\Desktop\\test.pdf', 'wb') as test:
            test.write(base64.b64decode(monthly_statements.FILEITEM))
        return send_file('C:\\Users\\Manomay\\Desktop\\test.pdf')
