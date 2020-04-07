import json
import os
import threading
from datetime import datetime
import time

import xlrd
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, RESPONSE_OK, delete_excel
from ...models import db, status, roles
from ...models.documents import Documents
from xlutils.copy import copy
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('user', type=str, location='args', required=True)
parser.add_argument('offset', type=int, location='args', required=True)

response_model_child = ns.model('GetGetdocumentsChild', {
    "FormID": fields.String,
    "EmployerID": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.String,
    "FileName": fields.String,
    "PendingFrom": fields.String
})

response_model = ns.model('GetGetdocuments', {
    "documents": fields.List(fields.Nested(response_model_child))
})


@ns.route("/get")
class Getdocument(Resource):
    @ns.doc(description='Get all the documents under an employer',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            return Unauthorized()
        offset_ = int(args["offset"])
        if offset_ is None or str(offset_) == "":
            offset_ = 0
        employer_id = args["user"]
        forms_data = []
        if decode_token['role'] in roles.ROLES_REVIEW_MANAGER:
            documents = Documents.query.order_by(Documents.LastModifiedDate.desc()).offset(offset_).limit(50).all()
        if decode_token['role'] in roles.ROLES_EMPLOYER:
            documents = Documents.query.filter_by(EmployerID=args['username'])\
                .order_by(Documents.LastModifiedDate.desc()).offset(offset_).limit(50).all()
        if documents is None:
            return {"documents": []}, 200
        for document in documents:
            forms_data.append({
                "FormID": document.FormID,
                "EmployerID": document.EmployerID,
                "FormType": "Document",
                "FormStatus": document.Status,
                "LastModifiedDate": document.LastModifiedDate,
                "PendingFrom": document.PendingFrom,
                "FileName": str(document.FilePath).replace("/", "\\").split("\\")[len(str(document.FilePath).replace("/", "\\").split("\\")) - 1] if document.FilePath is not None else ""
            })
        return {"documents": forms_data}, 200
