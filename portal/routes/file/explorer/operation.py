import os
import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, current_app as app
from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest, InternalServerError, Unauthorized, UnprocessableEntity
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from ....helpers import token_verify, delete_excel, RESPONSE_OK, token_verify_or_raise
from ....models import db, roles, status
from ....models.contributionform import Contributionform
from ....models.roles import *
from ....models.token import Token
from .. import ns
from .... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('request_type', type=str, location='form', required=True)
parser.add_argument('file', type=FileStorage, location='files', required=True)
parser.add_argument('foldername', type=str, location='form', required=True)
parser.add_argument('employerusername', type=str, location='form', required=True)


@ns.route("/explorer/operation")
class FileExplorerOperation(Resource):
    @ns.doc(description='File Explorer Operation',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        decoded_token = token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        if decoded_token['role'] != ROLES_EMPLOYER:
            raise Unauthorized()
        if args["request_type"] == "upload":
            if 'file' in request.files:
                print("hello")
                try:
                    employer_id = args["employerusername"]
                    path = APP.config["DATA_DIR"]
                    file = args['file']
                    foldername = args["foldername"]
                    path = os.path.join(path, foldername)
                    filename = secure_filename(file.filename)
                    print(filename)
                    filename = str(datetime.today().strftime("%Y%m%d %H%M%S.%f") + filename)
                    path = os.path.join(path, employer_id)
                    if not os.path.exists(path):
                        os.mkdir(path, mode=0o777)
                    file.save(os.path.join(path, filename))
                    return RESPONSE_OK
                except Exception as e:
                    LOG.error(e)
                    raise InternalServerError()
            else:
                raise BadRequest("No file found")
        else:
            UnprocessableEntity("Please enter valid info")


