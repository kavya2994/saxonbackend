import os
import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, current_app as app
from flask_restplus import Resource, reqparse
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from ... import APP
from ...helpers import token_verify, delete_excel, token_verify_or_raise, crossdomain
from ...models import db, roles
from ...models.settings import Settings
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('notification_email', type=str, location='json', required=True)
parser.add_argument('archive_days', type=str, location='json', required=True)
parser.add_argument('review_ip', type=str, location='json', required=True)
parser.add_argument('rm_ip', type=str, location='json', required=True)
parser.add_argument('last_run', type=str, location='json', required=True)
parser.add_argument('sync', type=str, location='json', required=True)


@ns.route("/settings/add")
class AddSettings(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Add settings',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_ADMIN:
            notify_email = args["notification_email"]
            archive_days = args["archive_days"]
            review_ip = args["review_ip"]
            rm_ip = args["rm_ip"]
            last_run = args["last_run"]
            sync = args["sync"]
            admin_settings = Settings(
                NotificationEmail=notify_email,
                ArchiveDays=archive_days,
                ReviewIP=review_ip,
                RMIP=rm_ip,
                LastRun=last_run,
                Sync=sync
            )
            try:
                db.session.add(admin_settings)
                db.session.commit()
                return {"result": "success"}, 200
            except Exception as e:
                print(str(e))
                raise InternalServerError(str(e))
        else:
            raise Unauthorized()
