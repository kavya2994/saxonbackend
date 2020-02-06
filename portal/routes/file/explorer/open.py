import os
import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from ....helpers import token_verify, delete_excel
from ....models import db
from ....models.token import Token
from .. import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('User', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/explorer/open")
class FileExplorerOpen(Resource):
    @ns.doc(parser=parser,
        description='File Explorer Open',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
        print(request.headers)
        path = request.args.get('path')
        print(path)
        return send_file(os.path.join(app.config['DATA_DIR'], path)), 200


@ns.route("/explorer/open/zip")
class FileExplorerOpen(Resource):
    @ns.doc(parser=parser,
        description='File Explorer Open',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
        if 'Authorization' in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            root = app.config['DATA_DIR']
            data = json.loads(str(request.data, encoding='utf-8'))
            print("-------------")
            print(data)
            root = os.path.join(root, data["request_folder"])
            path_ = os.path.join(app.config['DATA_DIR'], data["request_folder"])
            paths = list(data["path"])
            print(paths)

            # if not len(paths) == 1:
            time = datetime.utcnow().strftime("%d%m%Y%H%M%S%f")
            zip_file = zipfile.ZipFile(str(time) + ".zip", 'w')
            with zip_file:
                for path in paths:
                    finalpath = root + path
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
                    threading.Thread(target=delete_excel, args=(str(time) + '.zip',)).start()
                    return send_file(str(time) + '.zip', as_attachment=str(time) + '.zip')
        else:
            return jsonify({"error": "Not Authorized"}), 401
