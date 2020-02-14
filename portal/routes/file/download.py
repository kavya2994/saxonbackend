import os
import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from flask_restplus import Resource, reqparse
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from ...helpers import delete_excel
from ...models import db
from ...models.token import Token
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/download")
class FileDownload(Resource):
    @ns.doc(parser=parser,
        description='Download File',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
        root = app.config['DATA_DIR']
        data = json.loads(str(request.data, encoding='utf-8'))
        print("-------------")
        print(data)
        root = os.path.join(root, data["request_folder"])
        path_ = os.path.join(app.config['DATA_DIR'], data["request_folder"])
        paths = list(data["path"])
        print(paths)
        return send_file(os.path.join(path_, paths[0])), 200
