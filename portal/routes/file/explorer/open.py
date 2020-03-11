import os
import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from ....helpers import token_verify, delete_excel, token_verify_or_raise
from ....models import db
from ....models.token import Token
from .. import ns
from .... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('path', type=str, location='json', required=True)
parser.add_argument('requestfolder', type=str, location='json', required=True)


@ns.route("/explorer/open")
class FileExplorerOpen(Resource):
    @ns.doc(description='File Explorer Open',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        path = args["path"]
        requestfolder = args["requestfolder"]
        print(path)
        return send_file(os.path.join(APP.config['DATA_DIR'], requestfolder, path))

