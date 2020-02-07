import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from werkzeug.utils import secure_filename
from ...helpers import token_verify
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


# @enrollment_blueprint.route("/enrollment", methods=['GET', 'POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
@ns.route("/")
class EnrollmentFile(Resource):
    @ns.doc(parser=parser,
        description='Get Enrollment Data',
        responses={200: 'OK', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
        token_id = request.args["TokenID"]
        tokendata = Token.query.get(token_id)
        print(tokendata)
        if tokendata is not None:
            formdata = Enrollmentform.query.filter_by(tokenID=tokendata["TokenID"]).first()
            print(formdata)
            return {"result": formdata}, 200
        else:
            return {"error": "Bad Request"}, 400
