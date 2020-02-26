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
from ....helpers import token_verify, delete_excel, crossdomain, token_verify_or_raise
from ....models import db
from ....models.token import Token
from .. import ns
from .... import APP

zipparser = reqparse.RequestParser()
zipparser.add_argument('Authorization', type=str, location='headers', required=True)
zipparser.add_argument('username', type=str, location='headers', required=True)
zipparser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/explorer/open/zip")
class FileExplorerOpenZip(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=zipparser,
            description='File Explorer Open',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(zipparser, validate=True)
    def post(self):
        args = zipparser.parse_args()
        print(args)
        token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])
        root = APP.config['DATA_DIR']
        data = json.loads(str(request.data, encoding='utf-8'))
        request_folder = data["requestfolder"]
        root = os.path.join(root, request_folder)
        path_ = os.path.join(APP.config['DATA_DIR'], request_folder)
        paths = list(data["path"])
        print(paths)

        # if not len(paths) == 1:
        time = datetime.utcnow().strftime("%d%m%Y%H%M%S%f")
        zip_file = zipfile.ZipFile(os.path.join(APP.config['ZIP_DATA_DIR'], str(time) + ".zip"), 'w')
        with zip_file:
            for path in paths:
                finalpath = os.path.join(root, path)
                print(finalpath)
                if os.path.isfile(finalpath):
                    zip_file.write(finalpath)
                elif os.path.isdir(finalpath):
                    for r, d, f in os.walk(finalpath):
                        for folders in d:
                            zip_file.write(os.path.join(r, folders))
                        for files in f:
                            zip_file.write(os.path.join(r, files))
            zip_file.close()
            threading.Thread(target=delete_excel, args=(os.path.join(APP.config['ZIP_DATA_DIR'], str(time) + ".zip"),)).start()
            return send_file(os.path.join(APP.config['ZIP_DATA_DIR'], str(time) + ".zip"), as_attachment=str(time) + '.zip')
