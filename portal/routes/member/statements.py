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
    "FileName": fields.String
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
            annual_statements = AnnualStatements.query.filter_by(MEMNO=user).all()
            for statement in annual_statements:
                statements.append({
                    "DateFrom": statement.DATE_FROM,
                    "DateTo": statement.DATE_TO,
                    "FileName": statement.FILENAME
                })
        elif args["statementtype"] == "Monthly":
            monthly_statements = MonthlyStatements.query.filter_by(MEMNO=user).all()
            for statement in monthly_statements:
                statements.append({
                    "DateFrom": statement.DATE_FROM,
                    "DateTo": statement.DATE_TO,
                    "FileName": statement.FILENAME
                })

        else:
            raise BadRequest("Not a valid request")
        return {"Files": statements}, 200


@ns.route("/statement/get/<FileName>")
class GetStatements(Resource):
    @ns.doc(description='Get Statements',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def get(self, FileName):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        user = args['user']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token['role'] not in [ROLES_MEMBER, ROLES_REVIEW_MANAGER]:
            raise Unauthorized()
        if decoded_token['role'] == ROLES_MEMBER and username != user:
            raise Unauthorized()
        statemnt_type = args["statementtype"]
        if statemnt_type == "Monthly":
            monthly_statements = MonthlyStatements.query.filter_by(
                FILENAME=FileName, MEMNO=user).first()
            if monthly_statements is None:
                raise UnprocessableEntity("Not a valid file")
            filepath = os.path.join(APP.config["EXCEL_TEMPLATE_DIR"], FileName)
            file = open(filepath, 'wb')
            file.write(monthly_statements.FILEITEM)
            file.close()
            t = threading.Thread(target=delete_excel, args=(filepath,))
            t.start()
            return send_file(filepath)
        elif statemnt_type == "Annual":
            annual_statements = AnnualStatements.query.filter_by(
                FILENAME=FileName, MEMNO=user).first()
            if annual_statements is None:
                raise UnprocessableEntity("Not a valid file")
            filepath = os.path.join(APP.config["EXCEL_TEMPLATE_DIR"], FileName)
            file = open(filepath, 'wb')
            file.write(annual_statements.FILEITEM)
            file.close()
            t = threading.Thread(target=delete_excel, args=(filepath,))
            t.start()
            return send_file(filepath)
        else:
            raise BadRequest()
