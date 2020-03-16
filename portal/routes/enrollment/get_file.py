import argparse
import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse, fields, inputs, cors
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from werkzeug.utils import secure_filename

from ...helpers import token_verify_or_raise, RESPONSE_OK
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models.comments import Comments
from ...models.roles import *
from ...models import db, status
from ...models.status import *
from ...api import api
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/file/get/<TokenID>")
class GetFile(Resource):
    @ns.doc(description='Get all employers in b/w min and max',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def get(self, TokenID):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] != ROLES_REVIEW_MANAGER:
            raise Unauthorized()
        token = Token.query.get(TokenID)
        if token is None or token.TokenStatus != STATUS_ACTIVE or token.PendingFrom != ROLES_REVIEW_MANAGER:
            raise UnprocessableEntity("Not a Valid Token")

        form = Enrollmentform.query.get(token.FormID)
        if form is None:
            raise UnprocessableEntity("Not a valid Enrollment form")

        if form.FilePath is None:
            raise NotFound("File Not found")

        return send_file(form.FilePath)

