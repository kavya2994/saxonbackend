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
from ....helpers import token_verify, delete_excel
from ....models import db
from ....models.token import Token
from .. import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/explorer")
class FileExplorer(Resource):
    @ns.doc(parser=parser,
        description='File Explorer',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
        auth1 = request.headers["Authorization"]
        auth1 = jwt.decode(auth1, key=app.config['JWT_SECRET'])
        print(request+" get requesttt")
        data = json.loads(str(request.data, encoding='utf-8'))
        return send_file(os.path.join(app.config['DATA_DIR'], data["request_folder"])), 200


    @ns.doc(parser=parser,
        description='File Explorer',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                print('post dataa')
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key=app.config['JWT_SECRET'])
                data = json.loads(str(request.data, encoding='utf-8'))

                path = os.path.join(app.config['DATA_DIR'], data["request_folder"])
                folders = {}
                object_to_send = []
                id = 1
                # r=root, d=directories, f = files
                for r, d, f in os.walk(path):
                    # folders[parent] = {}
                    for folder in d:
                        p = r.split("\\")
                        parent = p[len(p) - 1]
                        if parent == '' or parent == data["request_folder"]:
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
                                if actual_parent == data["request_folder"]:
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
                        p = r.split("\\")
                        parent = p[len(p) - 1]
                        if parent == '':
                            parent = 'root'
                            # print(r.split("\\"))
                            object_to_send.append({"id": id, "name": file, "isFolder": False, "parent": 'root',
                                                   "modifiedtime": time.strftime('%Y-%m-%d %H:%M:%S',
                                                                                 time.localtime(os.path.getmtime(
                                                                                     os.path.join(r, file))))})
                            id += 1
                        else:

                            # print(p)
                            folder = p[len(p) - 2]
                            if folder == data["request_folder"]:
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
                return jsonify(object_to_send), 200
            except jwt.DecodeError:
                print("decode error")
                return jsonify({"error": "Un Authorised"}), 401
            except jwt.ExpiredSignatureError:
                print("sign")
                return jsonify({"error": "Un Authorised"}), 401
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500
        else:
            return jsonify({"error": "Un Authorised"}), 401
