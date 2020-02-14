import os
import jwt
import json
import smtplib
from functools import reduce
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, fields, inputs, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise
from ...models.beneficiary import Beneficiary, BeneficiaryResponseModel
from ...models.enrollmentform import Enrollmentform
from ...models.roles import *
from ...models import db
from ...api import api
from . import ns
from ... import APP


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

postParser = reqparse.RequestParser()
postParser.add_argument('Authorization', type=str, location='headers', required=True)
postParser.add_argument('Username', type=str, location='headers', required=True)
postParser.add_argument('IpAddress', type=str, location='headers', required=True)

postParser.add_argument('FirstName', type=str, location='json', required=True)
postParser.add_argument('LastName', type=str, location='json', required=True)
postParser.add_argument('DOB', type=inputs.date_from_iso8601, location='json', required=True, help='iso8601 format. eg: 2012-11-25')
postParser.add_argument('Relationship', type=str, location='json', required=True)
postParser.add_argument('Role', type=str, location='json', required=True)
postParser.add_argument('PhoneNumber', type=str, location='json', required=True)
postParser.add_argument('Percentage', type=float, location='json', required=True)


@ns.route("/form/<FormID>")
class BeneficiaryFormController(Resource):
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'])
    def options(self):
        pass

    @ns.doc(parser=parser,
        description='Get Beneficiary',
        responses={
            200: 'OK',
            401: 'Unauthorized',
            404: 'NotFound',
            500: 'Internal Server Error'
        })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(BeneficiaryResponseModel)
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'])
    def get(self, FormID):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['IpAddress'], user=args['Username'])

        if auth['Role'] not in [ROLES_EMPLOYER, ROLES_ADMIN]:
            raise Unauthorized()

        beneficiaries = Beneficiary.query.filter_by(EnrollmentformID=FormID).all()
        return beneficiaries


    @ns.doc(parser=postParser,
        description='Add New Beneficiary',
        responses={
            200: 'OK',
            404: 'BadRequest',
            401: 'Unauthorized',
            404: 'NotFound',
            500: 'Internal Server Error'
        })
    @ns.marshal_with(BeneficiaryResponseModel)
    @ns.expect(postParser, validate=True)
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'])
    def post(self, FormID):
        args = postParser.parse_args(strict=True)
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['IpAddress'], user=args['Username'])

        if auth['Role'] not in [ROLES_EMPLOYER, ROLES_ADMIN]:
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
            Role=args['Role'],
            PhoneNumber=args['PhoneNumber'],
            Percentage=args['Percentage'],
        )

        beneficaries = Beneficiary.query.filter_by(EnrollmentformID=FormID).all()
        total_percents = reduce(lambda acc, ben: acc+ben.Percentage, beneficaries, 0)

        if total_percents + args['Percentage'] > 100:
            raise BadRequest(f'Requested percentage is exceeding 100. Currently {total_percents}% are allocated.')

        db.session.add(beneficiary)
        db.session.commit()

        return Beneficiary.query.filter_by(EnrollmentformID=FormID).all()

    @ns.doc(parser=parser,
        description='Delete A Beneficiary',
        responses={
            200: 'OK',
            404: 'BadRequest',
            401: 'Unauthorized',
            404: 'NotFound',
            500: 'Internal Server Error'
        })
    @ns.marshal_with(BeneficiaryResponseModel)
    @ns.expect(parser, validate=True)
    @cors.crossdomain(origin=APP.config['CORS_ORIGIN_WHITELIST'])
    def delete(self, FormID):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args['Authorization'], ip=args['IpAddress'], user=args['Username'])

        if auth['Role'] not in [ROLES_EMPLOYER, ROLES_ADMIN]:
            raise Unauthorized()

        form = Enrollmentform.query.get(FormID)
        if form is None:
            raise BadRequest()

        pass
