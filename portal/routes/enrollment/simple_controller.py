import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, fields, inputs, cors
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, crossdomain
from ...models.enrollmentform import Enrollmentform, EnrollmentformResponseModel
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns
from ... import APP


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/<FormID>")
class SimpleEnrollmentController(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
        description='Get Enrollment Data by FormID',
        responses={
            200: 'OK',
            401: 'Unauthorized',
            404: 'NotFound',
            500: 'Internal Server Error'
        })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(EnrollmentformResponseModel)
    def get(self, FormID):
        args = parser.parse_args()
        auth = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        enrollmentform = Enrollmentform.query.get(FormID)

        if enrollmentform is None:
            raise NotFound

        return enrollmentform

