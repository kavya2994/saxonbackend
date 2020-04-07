import json
import os
import threading
from datetime import datetime
import time

import xlrd
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.datastructures import FileStorage
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

post_parser = reqparse.RequestParser()
post_parser.add_argument('Authorization', type=str, location='headers', required=True)
post_parser.add_argument('username', type=str, location='headers', required=True)
post_parser.add_argument('Ipaddress', type=str, location='headers', required=True)
post_parser.add_argument('Comment', type=str, location='form', required=False)
post_parser.add_argument('CommentName', type=str, location='form', required=False)
post_parser.add_argument("request_type", type=str, location='form', required=True)
post_parser.add_argument("filename", type=str, location='form', required=False)
post_parser.add_argument('employerusername', type=str, location='form', required=False)
post_parser.add_argument('employername', type=str, location='form', required=False)
post_parser.add_argument('file', type=FileStorage, location='files', required=False)

RequestType_SaveFormData = 'SaveFormData'
RequestType_ApprovalConfirmation = 'ApprovalConfirmation'
RequestType_Reject = 'Reject'
# RequestType_Delete = 'Delete'

response_model = ns.model('PostInitiateContribution', {
    'error': fields.String,
    'result': fields.String,
})
comments_model = ns.model('Comments', {
    "Name": fields.String,
    "Date": fields.String,
    "Comment": fields.String
})
get_response_model = ns.model('GetGetContributionsChild', {
    "FormID": fields.String,
    "EmployerID": fields.String,
    "FormType": fields.String,
    "PendingFrom": fields.String,
    "EmployerName": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "FileName": fields.String,
    "comments": fields.List(fields.Nested(comments_model))
})


@ns.route("/controller/<FormID>")
class DocumentsController(Resource):
    @ns.doc(parser=parser,
            description='Get Documents',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(get_response_model)
    def get(self, FormID):
        print("entered formid")
        args = parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_REVIEW_MANAGER, roles.ROLES_EMPLOYER]:
            return Unauthorized()

        document = Documents.query.filter_by(FormID=FormID).first()
        comments = Comments.query.filter_by(FormID=FormID, FormType="Documents").all()
        comments_list = []
        if document is not None:
            if comments is not None:
                for comment in comments:
                    comments_list.append({
                        "Name": comment.Name,
                        "Date": comment.Date,
                        "Comment": comment.Comment
                    })
            return {
                       "FormID": document.FormID,
                       "EmployerID": document.EmployerID,
                       "FormType": "Contribution",
                       "PendingFrom": document.PendingFrom,
                       "EmployerName": document.EmployerName,
                       "FormStatus": document.Status,
                       "LastModifiedDate": document.LastModifiedDate,
                       "FileName": str(document.FilePath).replace("/", "\\").split("\\")[len(str(document.FilePath).replace("/", "\\").split("\\")) - 1] if document.FilePath is not None else "",
                       "comments": comments_list
                   }, 200
        else:
            raise UnprocessableEntity("No contribution found with the requested Form data")

    @ns.doc(parser=post_parser,
            description='Documents Approval and Rejection',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(post_parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self, FormID):
        args = post_parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            return Unauthorized()

        document = Documents.query.filter_by(FormID=FormID).first()
        initiation_date = datetime.utcnow()
        if document is not None:
            if args["request_type"] == RequestType_SaveFormData:
                if decode_token["role"] == roles.ROLES_EMPLOYER:
                    if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                        comment = Comments(
                            FormID=FormID,
                            Name=args['CommentName'],
                            Role=roles.ROLES_EMPLOYER,
                            Comment=args['Comment'],
                            Date=initiation_date,
                            FormType="Documents"
                        )
                        db.session.add(comment)
                        db.session.commit()
                    return {"result": "Success"}, 200
                elif decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    path = APP.config['DATA_DIR']
                    userid = args["employerusername"]
                    employer_name = args["employername"]
                    if 'file' in request.files:
                        file = request.files['file']
                        filename = secure_filename(file.filename)
                        print(filename)
                        path = os.path.join(path, "Employers")
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, userid)
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, "Documents")
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, str(FormID))
                        if not os.path.exists(path):
                            os.mkdir(path)
                        file.save(os.path.join(path, filename))
                        document.FilePath = os.path.join(path, filename)
                    document.LastModifiedDate = initiation_date
                    db.session.commit()
                    if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                        comment = Comments(
                            FormID=FormID,
                            Name=args['CommentName'],
                            Role=roles.ROLES_REVIEW_MANAGER,
                            Comment=args['Comment'],
                            Date=initiation_date,
                            FormType="Documents"
                        )
                        db.session.add(comment)
                        db.session.commit()
                else:
                    raise Unauthorized()
            elif args["request_type"] == RequestType_ApprovalConfirmation:
                if decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    print("in approval")
                    path = APP.config['DATA_DIR']
                    userid = request.form["employerusername"]
                    print(document.FilePath)
                    if document.FilePath is None:
                        if 'file' in request.files:
                            file = request.files['file']
                            filename = secure_filename(file.filename)
                            print(filename)
                            path = os.path.join(path, "Employers")
                            if not os.path.exists(path):
                                os.mkdir(path)
                            path = os.path.join(path, userid)
                            if not os.path.exists(path):
                                os.mkdir(path)
                            path = os.path.join(path, "Documents")
                            if not os.path.exists(path):
                                os.mkdir(path)
                            path = os.path.join(path, str(FormID))
                            if not os.path.exists(path):
                                os.mkdir(path)
                            file.save(os.path.join(path, filename))
                            document.FilePath = os.path.join(path, filename)
                    if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                        comment = Comments(
                            FormID=FormID,
                            Name=args['CommentName'],
                            Role=roles.ROLES_REVIEW_MANAGER,
                            Comment=args['Comment'],
                            Date=initiation_date,
                            FormType="Documents"
                        )
                        db.session.add(comment)
                        db.session.commit()
                    document.LastModifiedDate = initiation_date
                    document.Status = status.STATUS_APPROVE
                    db.session.commit()
                else:
                    raise Unauthorized()
            elif args["request_type"] == RequestType_Reject:
                if decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    document.Status = status.STATUS_REJECT
                    if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                        comment = Comments(
                            FormID=FormID,
                            Name=args['CommentName'],
                            Role=roles.ROLES_REVIEW_MANAGER,
                            Comment=args['Comment'],
                            Date=initiation_date,
                            FormType="Documents"
                        )
                        db.session.add(comment)
                    db.session.commit()
                else:
                    raise Unauthorized()

            # elif args["request_type"] == RequestType_Delete:
            #     if not decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
            #         raise Unauthorized()
            #     file_path = document.FilePath
            #     if file_path is not None:
            #         if os.path.exists(file_path):
            #             os.remove(file_path)
            #             document.FilePath = None
            #             db.session.commit()
            #         else:
            #             raise UnprocessableEntity("Can't find file")
            #     else:
            #         raise UnprocessableEntity("Can't find filename")


            else:
                raise BadRequest()
            return RESPONSE_OK
