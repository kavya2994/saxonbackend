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
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/explorer/operation")
class FileExplorerOperation(Resource):
    @ns.doc(parser=parser,
        description='File Explorer Operation',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        print(request.headers)
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key='secret')
                path = app.config['DATA_DIR']
                file = request.files['file']
                print("----------------")
                print(request.form["request_type"])
                print("----------------")
                # print(file.filename)
                if request.form["request_type"] == "contribution":
                    startdate = request.form["startDate"]
                    enddate = request.form["endDate"]
                    print(startdate)
                    start_date = datetime.strptime(startdate, "%a %b %d %Y")
                    end_date = datetime.strptime(enddate, "%a %b %d %Y")
                    formtype = request.form["formType"]
                    userid = request.form["employerusername"]
                    employer = request.form["employer"]
                    path = os.path.join(root, "Employers")
                    if not os.path.exists(path):
                        os.mkdir(path)
                    path = os.path.join(path, userid)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    path = os.path.join(path, "contribution")
                    if not os.path.exists(path):
                        os.mkdir(path)
                    if 'file' in request.files:
                        print("hello")
                        filename = secure_filename(file.filename)
                        print(filename)
                        # filename = str(datetime.today().strftime("%Y%m%d %H%M%S.%f") + filename)
                        # myforms = db1.collection("myforms").add({"filename": filename, "startDate": start_date,
                        #                                          "endDate": end_date,
                        #                                          "employername": employer,
                        #                                          "employernumber": employer_id, "formType": formtype,
                        #                                          "formCreatedDate": datetime.utcnow(), "status": "pending",
                        #                                          "pendingFrom": "reviewer"})
                        # print(myforms[1].id)
                        token = Token(
                            # FormID=,
                            FormCreatedDate=datetime.utcnow(),
                            FormStatus="pending",
                            FormType=formtype,
                            InitiatedBy=userid,
                            # InitiatedDate=,
                            PendingFrom="reviewer",
                            TokenStatus="active",
                            EmployerID=userid,
                            # OlderTokenID=,
                        )
                        db.session.add(token)
                        db.session.commit()

                        path = os.path.join(path, str(token.TokenID))
                        if not os.path.exists(path):
                            os.mkdir(path)
                        file.save(os.path.join(path, filename))
                    else:
                        return jsonify({"error": "Bad request"}), 400

                    return jsonify({"result": "Success"}), 200
                elif request.form["request_type"] == "upload":
                    if 'file' in request.files:
                        print("hello")
                        try:
                            foldername = request.form["foldername"]
                            path = os.path.join(path, foldername)
                            filename = secure_filename(file.filename)
                            print(filename)
                            filename = str(datetime.today().strftime("%Y%m%d %H%M%S.%f") + filename)
                            # path += str(employer_id) + "/"
                            # if not os.path.exists(path):
                            #     os.mkdir(path)
                            file.save(os.path.join(path, filename))
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            jsonify({"error": "Bad Request"}), 400
                    return jsonify({"error": "No file found in the request"}), 400
            except Exception as e:
                print(str(e))
                return jsonify({"error": "Not Authorized"}), 401
        else:
            return jsonify({"error": "Not Authorized"}), 401
