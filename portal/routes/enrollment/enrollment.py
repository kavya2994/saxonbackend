
import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields, inputs
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify, token_verify_or_raise
from ...models.enrollmentform import Enrollmentform, EnrollmentformResponseModel
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/<FormID>")
class Token(Resource):
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
        auth = token_verify_or_raise(token=args["Authorization"], ip=args["IpAddress"], user=args["Username"])

        enrollmentform = Enrollmentform.query.get(FormID)

        if enrollmentform is None:
            raise NotFound

        return enrollmentform

