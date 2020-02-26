import os
import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, current_app as app
from flask_restx import Resource, reqparse, fields
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from ... import APP, LOG
from ...helpers import token_verify, delete_excel, token_verify_or_raise, crossdomain
from ...models import db, roles
from ...models.settings import Settings
from . import ns
from ...models.users import Users

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('user', type=str, location='args', required=True)

response_model = ns.model('GetGetUserData', {
    "Username": fields.String,
    "DisplayName": fields.String,
    "Email": fields.String
})


@ns.route("/userdata/get")
class GetUserData(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get user data',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        user = args["user"]
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_ADMIN:
            try:
                users = Users.query.filter_by(Username=user).first()
                if users is not None:
                    return {
                               "Username": users.Username,
                               "DisplayName": users.DisplayName,
                               "Email": users.Email,
                           }, 200
                else:
                    raise UnprocessableEntity("Can't find user")
            except Exception as e:
                LOG.error("Exception while getting user data", e)
                raise InternalServerError("Can't get user data")
        else:
            raise Unauthorized()
