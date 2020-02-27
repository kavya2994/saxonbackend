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
from werkzeug.utils import secure_filename
from xlutils.copy import copy

from .... import APP
from ....helpers import token_verify, delete_excel, token_verify_or_raise
from ....models import db
from ....models.token import Token
from .. import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/explorer/operations")
class FileExplorerOperations(Resource):
    @ns.doc(description='File Explorer Operations',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        data = json.loads(str(request.data, encoding='utf-8'))
        operation = data["operation"]
        print(operation)
        # request_folder = data["requestfolder"]
        path = os.path.join(app.config['DATA_DIR'], data["requestfolder"])
        if operation == "move":

            destination = os.path.join(path, data["destination"][0])
            try:
                for i in range(len(data["source"])):
                    source = os.path.join(path, data["source"][i])
                    shutil.move(source, destination)
                return {"result": "Success"}, 200
            except Exception as e:
                print(str(e))
                return {"error": "Something wrong happened"}, 500
        elif operation == "copy":
            destination = os.path.join(path, data["destination"][0])
            try:
                for i in range(len(data["source"])):
                    source = os.path.join(path, data["source"][i])
                    print(source)
                    print(destination)
                    len_of_source = len(source.split("/"))
                    if os.path.isdir(source):
                        shutil.copytree(source,
                                        os.path.join(destination, source.split("/")[len_of_source - 1]))
                    elif os.path.isfile(source):
                        shutil.copy(source, destination)
                    else:
                        return {"error": "Something wrong happened"}, 500
                    return {"result": "Success"}, 200
            except OSError as e:
                if isinstance(e, WindowsError) and e.winerror == 183:
                    return {"error": "Cannot create a file when that file already exists"}, 500
                elif isinstance(e, WindowsError) and e.winerror == 267:
                    return {"error": "Invalid file"}, 500
            except Exception as e:
                print(str(e))
                return {"error": "Something wrong happened"}, 500
        elif operation == "rename":
            print(data)
            result = []
            try:
                for i in range(len(list(data["source"]))):
                    source = os.path.join(path, data["source"][i])
                    destination = os.path.join(path, data["destination"][i])
                    os.rename(source, destination)
                return {"result": "Success"}, 200
            except Exception as e:
                print(str(e))
                return {"error": "Something wrong happened"}, 500
        elif operation == "delete":
            source = os.path.join(path, data["source"][0])
            print(source)
            try:
                if os.path.isdir(source):
                    print("in dir")
                    shutil.rmtree(source)
                elif os.path.isfile(source):
                    print("in file")
                    os.remove(source)
                else:
                    return {"error": "Couldn't find the file or folder"}, 404
                return {"result": "Success"}, 200
            except Exception as e:
                print(str(e))
                return {"error": "Something wrong happened"}, 500
        elif operation == "upload":
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(os.path.join(path, filename))
            return jsonify({"result": "Success"}), 200
            # return send_file(os.path.join(path, filename))
        elif operation == "createnewfolder":
            folder_path = os.path.join(path, data["source"])
            try:
                os.mkdir(folder_path)
                return {"result": "Success"}, 200
            except Exception as e:
                print(str(e))
                return {"error": "Can't create folder"}, 500

