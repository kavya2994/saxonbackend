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
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, InternalServerError, NotFound
from werkzeug.utils import secure_filename
from xlutils.copy import copy

from ... import APP, LOG
from ...helpers import delete_excel, token_verify_or_raise
from ...models import db
from ...models.token import Token
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('requestfolder', type=str, location='json', required=True)
parser.add_argument('path', type=str, location='json', required=True)


@ns.route("/download")
class FileDownload(Resource):
    @ns.doc(description='Download File',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error',
                       404: "Not Found"})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        try:
            root = app.config['DATA_DIR']
            data = json.loads(str(request.data, encoding='utf-8'))
            root = os.path.join(root, data["requestfolder"])
            path_ = os.path.join(app.config['DATA_DIR'], data["requestfolder"])
            paths = list(data["path"])
            if not os.path.exists(os.path.join(path_, paths[0])):
                raise NotFound("File not found")
            return send_file(os.path.join(path_, paths[0]), as_attachment=True)
        except Exception as e:
            LOG.error("Exception While Downloading File", e)
            raise InternalServerError("Unable to download the Requested file")
