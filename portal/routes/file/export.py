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
from ...helpers import token_verify, delete_excel
from ...models import db
from ...models.token import Token
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/export")
class FileExport(Resource):
    @ns.doc(parser=parser,
        description='Export Contribution File in XLS format',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def get(self):
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
