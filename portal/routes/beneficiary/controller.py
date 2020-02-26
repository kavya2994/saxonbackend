import os
import jwt
import json
import smtplib
from functools import reduce
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse, fields, inputs, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, crossdomain, RESPONSE_OK
from ...models.beneficiary import Beneficiary
from ...models.enrollmentform import Enrollmentform
from ...models.roles import *
from ...models import db
from ...api import api
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)

postParser = reqparse.RequestParser()
postParser.add_argument('Authorization', type=str, location='headers', required=True)
postParser.add_argument('username', type=str, location='headers', required=True)
postParser.add_argument('Ipaddress', type=str, location='headers', required=True)

postParser.add_argument('FirstName', type=str, location='json', required=True)
postParser.add_argument('LastName', type=str, location='json', required=True)
postParser.add_argument('DOB', type=inputs.date_from_iso8601, location='json', required=True,
                        help='iso8601 format. eg: 2012-11-25')
postParser.add_argument('Relationship', type=str, location='json', required=True)
postParser.add_argument('Role', type=str, location='json', required=True)
postParser.add_argument('PhoneNumber', type=str, location='json', required=True)
postParser.add_argument('Percentage', type=float, location='json', required=True)

deleteParser = reqparse.RequestParser()
deleteParser.add_argument('Authorization', type=str, location='headers', required=True)
deleteParser.add_argument('username', type=str, location='headers', required=True)
deleteParser.add_argument('Ipaddress', type=str, location='headers', required=True)
deleteParser.add_argument('BeneficiaryID', type=str, location='json', required=True)


beneficiary_response_model = ns.model('BeneficiaryResponseModel', {
    'BeneficiaryID': fields.String,
    'EnrollmentformID': fields.String,
    'FirstName': fields.String,
    'LastName': fields.String,
    'DOB': fields.Date,
    'Relationship': fields.String,
    'Role': fields.String,
    'PhoneNumber': fields.String,
    'Percentage': fields.Float,
})

beneficiary_list_response_model = ns.model('BeneficiaryListResponseModel', {
    'beneficiaries': fields.List(fields.Nested(beneficiary_response_model)),
})

response_model_ok = ns.model('DeleteBeneficiaryFormController', {
    "result": fields.String,
})

@ns.route("/form/<FormID>")
class BeneficiaryFormController(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get Beneficiary',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(beneficiary_list_response_model)
    def get(self, FormID):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] not in [ROLES_EMPLOYER, ROLES_ADMIN]:
            raise Unauthorized()

        beneficiaries = Beneficiary.query.filter_by(EnrollmentformID=FormID).all()
        return beneficiaries

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=postParser,
            description='Add New Beneficiary',
            responses={
                200: 'OK',
                404: 'BadRequest',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.marshal_with(beneficiary_list_response_model)
    @ns.expect(postParser, validate=True)
    def post(self, FormID):
        args = postParser.parse_args(strict=True)
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] not in [ROLES_EMPLOYER, ROLES_ADMIN]:
            raise Unauthorized()

        form = Enrollmentform.query.get(FormID)
        if form is None:
            raise NotFound()

        if args['Percentage'] <= 0:
            raise BadRequest('Invalid Percentage')

        beneficiary = Beneficiary(
            EnrollmentformID=FormID,
            FirstName=args['FirstName'],
            LastName=args['LastName'],
            DOB=args['DOB'],
            Relationship=args['Relationship'],
            Role=args['role'],
            PhoneNumber=args['PhoneNumber'],
            Percentage=args['Percentage'],
        )

        beneficaries = Beneficiary.query.filter_by(EnrollmentformID=FormID).all()
        total_percents = reduce(lambda acc, ben: acc + ben.Percentage, beneficaries, 0)

        if total_percents + args['Percentage'] > 100:
            raise BadRequest(f'Requested percentage is exceeding 100. Currently {total_percents}% are allocated.')

        db.session.add(beneficiary)
        db.session.commit()

        return Beneficiary.query.filter_by(EnrollmentformID=FormID).all()

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=deleteParser,
            description='Delete A Beneficiary',
            responses={
                200: 'OK',
                400: 'BadRequest',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.marshal_with(response_model_ok)
    @ns.expect(deleteParser, validate=True)
    def delete(self, FormID):
        args = deleteParser.parse_args(strict=True)
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])

        if auth['role'] not in [ROLES_EMPLOYER, ROLES_ADMIN]:
            raise Unauthorized()

        form = Enrollmentform.query.get(FormID)
        if form is None:
            raise NotFound('Form Not Found')

        beneficiary = Beneficiary.query.get(BeneficiaryID=args['BeneficiaryID'])
        if beneficiary is None:
            raise NotFound('Beneficiary Not Found')

        db.session.delete(beneficiary)
        db.session.commit()
        return RESPONSE_OK
