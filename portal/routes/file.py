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
from werkzeug.utils import secure_filename
from xlutils.copy import copy
from ..helpers import token_verify, delete_excel
from ..models import db
from ..models.token import Token


file_blueprint = Blueprint('file_blueprint', __name__, template_folder='templates')

@file_blueprint.route('/file', methods=["POST"])
def files_():
    if 'file' in request.files:
        file = request.files['file']
        print("hello")
        filename = secure_filename(file.filename)
        print(filename)

        file.save(os.path.join(filename))
        return "success", 200


@file_blueprint.route("/file_explorer", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer():
    if request.method == "POST":
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                print('post dataa')
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key='secret')
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
    if request.method == 'GET':
        auth1 = request.headers["Authorization"]
        auth1 = jwt.decode(auth1, key='secret')
        print(request+" get requesttt")
        data = json.loads(str(request.data, encoding='utf-8'))
        return send_file(os.path.join(app.config['DATA_DIR'], data["request_folder"])), 200


@file_blueprint.route("/download_file", methods=["POST", "OPTIONS"])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def download():
    if request.method == "POST":
        root = app.config['DATA_DIR']
        data = json.loads(str(request.data, encoding='utf-8'))
        print("-------------")
        print(data)
        root = os.path.join(root, data["request_folder"])
        path_ = os.path.join(app.config['DATA_DIR'], data["request_folder"])
        paths = list(data["path"])
        print(paths)
        return send_file(os.path.join(path_, paths[0])), 200


@file_blueprint.route("/file_explorer_open", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer_open():
    if request.method == "POST":
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
        # elif len(paths) == 1:
        #     folder = str(path_ + paths[0]).split("/")
        #     if os.path.isdir(path_ + paths[0]):
        #         return send_file(
        #             shutil.make_archive(folder[len(folder) - 1], 'zip', path_ + paths[0])
        #             , folder[len(folder) - 1]), 200
        #     elif os.path.isfile(path_ + paths[0]):
        #         return send_file(path_ + paths[0]), 200
        #     else:
        #         jsonify({"error": "No file found"}), 404
    if request.method == 'GET':
        print(request.headers)
        path = request.args.get('path')
        print(path)
        return send_file(os.path.join(app.config['DATA_DIR'], path)), 200


@file_blueprint.route("/file_explorer_operation", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origin=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
            'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer_operation():
    if request.method == "POST":
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
                            # formID=,
                            formCreatedDate=datetime.utcnow(),
                            formStatus="pending",
                            formType=formtype,
                            initiatedBy=userid,
                            # initiatedDate=,
                            pendingFrom="reviewer",
                            tokenStatus="active",
                            employerID=userid,
                            # olderTokenID=,
                        )
                        db.session.add(token)
                        db.session.commit()

                        path = os.path.join(path, str(token.id))
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

            # os.mkdir

        # return "hello", 200


@file_blueprint.route("/file_explorer_operations", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def file_explorer_operations():
    if request.method == "POST":
        print("---------------operations_headers---------------")
        print(request.headers)
        print("---------------operations_headers---------------")
        if "Authorization" in request.headers.keys():
            if token_verify(token=request.headers["Authorization"], ip=request.headers["Ipaddress"],
                            user=request.headers["User"]):
                try:
                    auth1 = request.headers["Authorization"]
                    auth1 = jwt.decode(auth1, key='secret')
                    data = json.loads(str(request.data, encoding='utf-8'))
                    operation = data["operation"]
                    print(operation)
                    path = os.path.join(app.config['DATA_DIR'], data["request_folder"])
                    if operation == "move":

                        destination = os.path.join(path, data["destination"][0])
                        try:
                            for i in range(len(data["source"])):
                                source = os.path.join(path, data["source"][i])
                                shutil.move(source, destination)
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
                    elif operation == "copy":
                        destination = os.path.join(path, data["destination"][0])
                        try:
                            for i in range(len(data["source"])):
                                source = os.path.join(path, data["source"][i])
                                print(source)
                                print(destination)
                                len_of_source = len(source.split("/"))
                                if os.path.isdir(source):
                                    shutil.copytree(source, os.path.join(destination, source.split("/")[len_of_source - 1]))
                                elif os.path.isfile(source):
                                    shutil.copy(source, destination)
                                else:
                                    return jsonify({"error": "Something wrong happened"}), 500
                                return jsonify({"result": "Success"}), 200
                        except OSError as e:
                            if isinstance(e, WindowsError) and e.winerror == 183:
                                return jsonify({"error": "Cannot create a file when that file already exists"}), 500
                            elif isinstance(e, WindowsError) and e.winerror == 267:
                                return jsonify({"error": "Invalid file"}), 500
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
                    elif operation == "rename":
                        print(data)
                        result = []
                        try:
                            for i in range(len(list(data["source"]))):
                                source = os.path.join(path, data["source"][i])
                                destination = os.path.join(path, data["destination"][i])
                                os.rename(source, destination)
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
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
                                return jsonify({"error": "Couldn't find the file or folder"}), 404
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Something wrong happened"}), 500
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
                            return jsonify({"result": "Success"}), 200
                        except Exception as e:
                            print(str(e))
                            return jsonify({"error": "Can't create folder"}), 500
                except Exception as e:
                    print(str(e))
                    return jsonify({"error": "bad request"}), 400
            else:
                return jsonify({"error": "Un Authorised"}), 401
        else:
            return jsonify({"error": "Un Authorised"}), 401
    return ""


@file_blueprint.route("/buildexcel", methods=["POST", "OPTIONS"])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'user', 'ipaddress'])
def build_excel():
    if request.method == "POST":
        print(request.headers)
        print(request.data)

        data = json.loads(str(request.data, encoding='utf-8'))
        employer_username = data["username"]
        employer_name = data["employername"]

        current_datetime = datetime.today()
        rb = xlrd.open_workbook('Contributionex.xls', formatting_info=True)

        wb = copy(rb)

        w_sheet = wb.get_sheet(0)

        w_sheet.write(9, 1, employer_name)
        w_sheet.write(9, 5, employer_username)

        employers = db1.collection("employers").document(employer_username)
        empuser = db1.collection("members").where("employers", "array_contains", employers).stream()

        i = 16
        for doc in empuser:
            print(doc.to_dict())
            member_details = doc.to_dict()
            w_sheet.write(i, 0, member_details["member_id"])
            w_sheet.write(i, 1, member_details["displayname"])
            i += 1
        filename = current_datetime.strftime("%d%m%Y %H%M%S") + 'Contribution.xls'
        wb.save(filename)
        t = threading.Thread(target=delete_excel, args=(filename,))
        t.start()
        time.sleep(3)
        return send_file(filename), 200

