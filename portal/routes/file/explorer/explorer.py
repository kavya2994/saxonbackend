import os
import time

import jwt
import json
import xlrd
import shutil
import threading
import zipfile
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, current_app as app
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
parser.add_argument('requestfolder', type=str, location='json', required=True)

get_parser = reqparse.RequestParser()
get_parser.add_argument('Authorization', type=str, location='headers', required=True)
get_parser.add_argument('username', type=str, location='headers', required=True)
get_parser.add_argument('Ipaddress', type=str, location='headers', required=True)
get_parser.add_argument('requestfolder', type=str, location='args', required=True)


@ns.route("/explorer")
class FileExplorer(Resource):
    @ns.doc(parser=get_parser,
            description='File Explorer',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(get_parser, validate=True)
    def get(self):

        print(request + " get requesttt")
        data = json.loads(str(request.data, encoding='utf-8'))
        return send_file(os.path.join(app.config['DATA_DIR'], data["requestfolder"])), 200

    @ns.doc(parser=parser,
            description='File Explorer',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args()
        request_folder = args["requestfolder"]
        # print(request_folder)
        # print('post dataa')
        token_verify_or_raise(token=args["Authorization"], user=args["username"], ip=args["Ipaddress"])

        path = os.path.join(app.config['DATA_DIR'], request_folder)
        folders = {}
        object_to_send = []
        id = 1
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            # folders[parent] = {}
            for folder in d:

                r = r.replace("\\", "/")
                p = r.split("/")
                parent = p[len(p) - 1]

                if parent == '' or parent == request_folder:
                    parent = 'root'
                    # print(r.split("\\"))
                    if parent not in folders.keys():
                        folders[parent] = {}
                    object_to_send.append({"id": id, "name": folder, "isFolder": True,
                                           "parent": 'root',
                                           "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                         time.localtime(os.path.getmtime(
                                                                             os.path.join(r, folder))))})
                    folders[parent][folder] = id
                    id += 1
                else:
                    if parent not in folders.keys():
                        folders[parent] = {}
                        # print(folders)
                    if folder not in folders[parent]:
                        actual_parent = p[len(p) - 2]
                        if actual_parent == request_folder:
                            actual_parent = 'root'
                        object_to_send.append({"id": id, "name": folder, "isFolder": True,
                                               "parent": folders[actual_parent][parent],
                                               "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                             time.localtime(os.path.getmtime(
                                                                                 os.path.join(r, folder))))})
                        folders[parent][folder] = id
                        id += 1
            # print(folders)
            for file in f:
                # files.append(os.path.join(r, file))
                # print(r)
                r = r.replace("\\", "/")
                p = r.split("/")
                parent = p[len(p) - 1]
                # print(parent)
                if parent == '' or parent == request_folder:
                    # parent = 'root'
                    # print(r.split("\\"))
                    object_to_send.append({"id": id, "name": file, "isFolder": False, "parent": 'root',
                                           "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                         time.localtime(os.path.getmtime(
                                                                             os.path.join(r, file))))})
                    id += 1

                else:

                    # print(p)
                    folder = p[len(p) - 2]
                    if folder == request_folder:
                        folder = 'root'
                    # print(parent)
                    # print(folder)
                    object_to_send.append(
                        {"id": id, "name": file, "isFolder": False, "parent": folders[folder][parent],
                         "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                       time.localtime(
                                                           os.path.getmtime(os.path.join(r, file))))})
                    id += 1

        print(object_to_send)
        return {"paths": object_to_send}, 200
