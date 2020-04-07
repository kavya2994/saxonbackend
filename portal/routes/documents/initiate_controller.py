import json
import os
import threading
from datetime import datetime
import time

import sqlalchemy
from cx_Oracle import IntegrityError
from werkzeug.datastructures import FileStorage
import xlrd
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from werkzeug.utils import secure_filename

from ...helpers import token_verify_or_raise, RESPONSE_OK, delete_excel
from ...models import db, status, roles
from ...models.comments import Comments
from ...models.documents import Documents
from ...models.member_view import MemberView
from ...models.employer_view import EmployerView
from xlutils.copy import copy
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('employerusername', type=str, location='form', required=True)
parser.add_argument('employername', type=str, location='form', required=True)
parser.add_argument('Comment', type=str, location='form', required=False)
parser.add_argument('file', type=FileStorage, location='files', required=True)

response_model = ns.model('PostInitiateDocuments', {
    'error': fields.String,
    'result': fields.String,
})


@ns.route("/initiate")
class InitiateDocument(Resource):
    @ns.doc(parser=parser,
            description='Uploads a files and initiate contribution',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            return Unauthorized()
        path = APP.config['DATA_DIR']
        file = request.files['file']
        initiation_date = datetime.utcnow()
        userid = request.form["employerusername"]
        employer_name = request.form["employername"]
        path = os.path.join(path, "Employers")
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, userid)
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, "documents")
        if not os.path.exists(path):
            os.mkdir(path)
        if 'file' in request.files:
            filename = secure_filename(file.filename)
            print(filename)
            try:
                document = Documents(
                    EmployerName=request.form["employername"],
                    Status=status.STATUS_PENDING,
                    Date=initiation_date,
                    PendingFrom=roles.ROLES_REVIEW_MANAGER,
                    EmployerID=request.form["employerusername"],
                    LastModifiedDate=initiation_date,
                )
                db.session.add(document)
                db.session.commit()

                path = os.path.join(path, str(document.FormID))
                if not os.path.exists(path):
                    os.mkdir(path)
                file.save(os.path.join(path, filename))
                document.FilePath = os.path.join(path, filename)
                db.session.commit()
            except IntegrityError as e:
                LOG.error("Error in contribution initiation form id integrity error", e)
                raise InternalServerError("Can't initiate Contribution")
            except Exception as e:
                LOG.error("Error in contribution initiation", e)
                raise InternalServerError("Can't initiate Contribution")
        else:
            return {"error": "Bad request"}, 400

        return {"result": "Success"}, 200
