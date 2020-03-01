import os
import jwt
import json
import smtplib
from functools import reduce
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, fields, inputs, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models.beneficiary import Beneficiary
from ...models.enrollmentform import Enrollmentform
from ...models.roles import *
from ...models.status import *
from ...models import db
from ...api import api
from . import ns
from ... import APP, LOG
from ...models.token import Token

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=False)
parser.add_argument('username', type=str, location='headers', required=False)
parser.add_argument('Ipaddress', type=str, location='headers', required=False)

postParser = reqparse.RequestParser()
postParser.add_argument('Authorization', type=str, location='headers', required=False)
postParser.add_argument('username', type=str, location='headers', required=False)
postParser.add_argument('Ipaddress', type=str, location='headers', required=False)

# postParser.add_argument('FirstName', type=str, location='json', required=True)
# postParser.add_argument('LastName', type=str, location='json', required=True)
# postParser.add_argument('DOB', type=inputs.date_from_iso8601, location='json', required=True,
#                         help='iso8601 format. eg: 2012-11-25')
# postParser.add_argument('Relationship', type=str, location='json', required=True)
# postParser.add_argument('Percentage', type=float, location='json', required=True)
postParser.add_argument('beneficiaries', type=list, location='json', required=False)

deleteParser = reqparse.RequestParser()
deleteParser.add_argument('Authorization', type=str, location='headers', required=False)
deleteParser.add_argument('username', type=str, location='headers', required=False)
deleteParser.add_argument('Ipaddress', type=str, location='headers', required=False)
deleteParser.add_argument('BeneficiaryID', type=str, location='args', required=True)

putParser = reqparse.RequestParser()
putParser.add_argument('Authorization', type=str, location='headers', required=False)
putParser.add_argument('username', type=str, location='headers', required=False)
putParser.add_argument('Ipaddress', type=str, location='headers', required=False)
putParser.add_argument('FirstName', type=str, location='json', required=True)
putParser.add_argument('LastName', type=str, location='json', required=True)
putParser.add_argument('DOB', type=inputs.date_from_iso8601, location='json', required=True,
                       help='iso8601 format. eg: 2012-11-25')
putParser.add_argument('Relationship', type=str, location='json', required=True)
putParser.add_argument('Percentage', type=float, location='json', required=True)
putParser.add_argument('BeneficiaryID', type=str, location='json', required=True)

beneficiary_response_model = ns.model('BeneficiaryResponseModel', {
    'BeneficiaryID': fields.String,
    'EnrollmentformID': fields.String,
    'FirstName': fields.String,
    'LastName': fields.String,
    'DOB': fields.Date,
    'Relationship': fields.String,
    'Role': fields.String,
    'Percentage': fields.Float,
})

beneficiary_list_response_model = ns.model('BeneficiaryListResponseModel', {
    'beneficiaries': fields.List(fields.Nested(beneficiary_response_model)),
})

response_model_ok = ns.model('DeleteBeneficiaryFormController', {
    "result": fields.String,
})


@ns.route("/token/<TokenID>")
class BeneficiaryFormController(Resource):
    @ns.doc(description='Get Beneficiary',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(beneficiary_list_response_model)
    def get(self, TokenID):
        args = parser.parse_args()
        token_data = Token.query.filter_by(TokenID=TokenID).first()
        if token_data is None:
            raise UnprocessableEntity("Can't find benficiary details")
        if not token_data.PendingFrom == ROLES_MEMBER:
            print(args["Authorization"])
            auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])
            if auth['role'] not in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
                raise Unauthorized()

        beneficiaries = Beneficiary.query.filter_by(EnrollmentformID=token_data.FormID).all()
        if beneficiaries is None:
            raise UnprocessableEntity("No beneficiaries found")

        return {"beneficiaries": beneficiaries}

    @ns.doc(description='Add New Beneficiary',
            responses={
                200: 'OK',
                400: 'BadRequest',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.marshal_with(beneficiary_list_response_model)
    @ns.expect(postParser, validate=True)
    def post(self, TokenID):
        args = postParser.parse_args(strict=True)
        token_data = Token.query.filter_by(TokenID=TokenID).first()
        if token_data is None:
            raise UnprocessableEntity("Can't find benficiary details")
        if not token_data.PendingFrom == ROLES_MEMBER:
            print(args["Authorization"])
            auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])
            if auth['role'] != ROLES_REVIEW_MANAGER:
                raise Unauthorized()

        FormID = token_data.FormID
        form = Enrollmentform.query.get(FormID)
        if form is None:
            raise NotFound()

        # if args['Percentage'] <= 0:
        #     raise BadRequest('Invalid Percentage')
        beneficiary_list = args["beneficiaries"]
        print(beneficiary_list)
        total = reduce(lambda a, ben: a + float(ben['Percentage']), beneficiary_list, 0)

        if total != 100:
            raise BadRequest("Invalid Percentage")

        for benef in beneficiary_list:
            print(type(benef['DOB']))
            dob_date = datetime.strptime(benef['DOB'], "%Y-%m-%d")
            if 'BeneficiaryID' not in benef.keys():
                beneficiary = Beneficiary(
                    EnrollmentformID=FormID,
                    FirstName=benef['FirstName'],
                    LastName=benef['LastName'],
                    DOB=dob_date,
                    Relationship=benef['Relationship'],
                    Role=ROLES_MEMBER,
                    Percentage=float(benef['Percentage']),
                )

                # beneficaries = Beneficiary.query.filter_by(EnrollmentformID=FormID).all()
                # total_percents = reduce(lambda acc, ben: acc + ben.Percentage, beneficaries, 0)
                #
                # if total_percents + args['Percentage'] > 100:
                #     raise BadRequest(f'Requested percentage is exceeding 100. Currently {total_percents}% are allocated.')

                db.session.add(beneficiary)
        db.session.commit()

        return Beneficiary.query.filter_by(EnrollmentformID=FormID).all()

    @ns.doc(description='Delete A Beneficiary',
            responses={
                200: 'OK',
                400: 'BadRequest',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.marshal_with(response_model_ok)
    @ns.expect(deleteParser, validate=True)
    def delete(self, TokenID):
        args = deleteParser.parse_args(strict=True)
        token = Token.query.get(TokenID)
        if token is None:
            raise UnprocessableEntity("Can't find benficiary details")
        if not token.PendingFrom == ROLES_MEMBER:
            print(args["Authorization"])
            auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])
            if auth['role'] not in [ROLES_EMPLOYER, ROLES_REVIEW_MANAGER]:
                raise Unauthorized()
        form = Enrollmentform.query.get(token.FormID)
        if form is None:
            raise NotFound('Form Not Found')

        beneficiary = Beneficiary.query.get(args['BeneficiaryID'])
        if beneficiary is None:
            raise NotFound('Beneficiary Not Found')

        db.session.delete(beneficiary)
        db.session.commit()
        return RESPONSE_OK

    @ns.doc(description='Delete A Beneficiary',
            responses={
                200: 'OK',
                400: 'BadRequest',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.marshal_with(response_model_ok)
    @ns.expect(deleteParser, validate=True)
    def put(self, TokenID):
        args = putParser.parse_args(strict=True)
        token = Token.query.get(TokenID)
        auth = None
        if token is None:
            raise UnprocessableEntity("Can't find benficiary details")
        if token.TokenStatus != STATUS_ACTIVE:
            raise NotFound("Not a valid Token")
        if not (token.PendingFrom == ROLES_MEMBER or token.TokenStatus == STATUS_ACTIVE):
            print(args["Authorization"])
            auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])
            if auth['role'] != ROLES_REVIEW_MANAGER:
                raise Unauthorized()
        try:
            beneficiary = Beneficiary.query.get(args['BeneficiaryID'])
            if beneficiary is None:
                raise NotFound('Beneficiary Not Found')
            # dob_date = datetime.strptime(args['DOB'], "%Y-%m-%d")
            print(type(args["DOB"]))
            beneficiary.FirstName = args["FirstName"]
            beneficiary.LastName = args["LastName"]
            beneficiary.Relationship = args["Relationship"]
            beneficiary.DOB = args['DOB']
            beneficiary.Percentage = float(args["Percentage"])
            beneficiary.Role = ROLES_MEMBER if auth is None else auth["role"]

            db.session.commit()
            return RESPONSE_OK
        except Exception as e:
            LOG.error("Exception while updating beneficiary", e)
            raise InternalServerError("Can't update beneficiary")
