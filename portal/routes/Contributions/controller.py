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
from ...models.contributionform import Contributionform
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
post_parser.add_argument("request_type", type=str, location='form', required=False)
post_parser.add_argument("filename", type=str, location='form', required=False)
post_parser.add_argument('employerusername', type=str, location='form', required=False)
post_parser.add_argument('employername', type=str, location='form', required=False)
post_parser.add_argument('startDate', type=str, location='form', required=False)
post_parser.add_argument('endDate', type=str, location='form', required=False)
post_parser.add_argument('file', type=FileStorage, location='files', required=False)

RequestType_SaveFormData = 'SaveFormData'
RequestType_ApprovalConfirmation = 'ApprovalConfirmation'
RequestType_Reject = 'Reject'
RequestType_Delete = 'Delete'

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
    "StartDate": fields.String,
    "PendingFrom": fields.String,
    "EmployerName": fields.String,
    "EndDate": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.DateTime,
    "FileName": fields.String,
    "comments": fields.List(fields.Nested(comments_model))
})


@ns.route("/controller/<FormID>")
class ContributionController(Resource):
    @ns.doc(parser=parser,
            description='Get Beneficiary',
            responses={
                200: 'OK',
                401: 'Unauthorized',
                404: 'NotFound',
                500: 'Internal Server Error'
            })
    @ns.expect(parser, validate=True)
    @ns.marshal_with(get_response_model)
    def get(self, FormID):
        args = parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_REVIEW_MANAGER, roles.ROLES_EMPLOYER]:
            return Unauthorized()

        contributions = Contributionform.query.filter_by(FormID=FormID).first()
        comments = Comments.query.filter_by(FormID=FormID).all()
        comments_list = []
        if contributions is not None:
            if comments is not None:
                for comment in comments:
                    comments_list.append({
                        "Name": comment.Name,
                        "Date": comment.Date,
                        "Comment": comment.Comment
                    })
            return {
                       "FormID": contributions.FormID,
                       "EmployerID": contributions.EmployerID,
                       "FormType": "Contribution",
                       "StartDate": contributions.StartDate,
                       "PendingFrom": contributions.PendingFrom,
                       "EmployerName": contributions.EmployerName,
                       "EndDate": contributions.EndDate,
                       "FormStatus": contributions.Status,
                       "LastModifiedDate": contributions.LastModifiedDate,
                       "FileName": str(contributions.FilePath).split("\\")[
                           len(str(contributions.FilePath).split(
                               "\\")) - 1] if contributions.FilePath is not None else "",
                       "comments": comments_list
                   }, 200
        else:
            raise UnprocessableEntity("No contribution found with the requested Form data")

    @ns.doc(parser=post_parser,
            description='Contribution Approval and Rejection',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(post_parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self, FormID):
        args = post_parser.parse_args()
        decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'],
                                             user=args['username'])
        if not decode_token['role'] in [roles.ROLES_EMPLOYER, roles.ROLES_REVIEW_MANAGER]:
            return Unauthorized()

        contribution = Contributionform.query.filter_by(FormID=FormID).first()
        initiation_date = datetime.utcnow()
        if contribution is not None:
            if args["request_type"] == RequestType_SaveFormData:
                if decode_token["role"] == roles.ROLES_EMPLOYER:
                    if 'Comment' in args and args['Comment'] != '':
                        comment = Comments(
                            FormID=FormID,
                            Name=args['CommentName'],
                            Role=roles.ROLES_EMPLOYER,
                            Comment=args['Comment'],
                            Date=initiation_date,
                        )
                        db.session.add(comment)
                        db.session.commit()
                    return {"result": "Success"}, 200
                elif decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    path = APP.config['DATA_DIR']
                    file = request.files['file']
                    startdate = args["startDate"]
                    enddate = args["endDate"]
                    start_date = datetime.strptime(startdate, "%a %b %d %Y")
                    end_date = datetime.strptime(enddate, "%a %b %d %Y")
                    userid = request.form["employerusername"]
                    employer_name = request.form["employername"]
                    if 'file' in request.files:
                        filename = secure_filename(file.filename)
                        print(filename)
                        path = os.path.join(path, "Employers")
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, userid)
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, "contribution")
                        if not os.path.exists(path):
                            os.mkdir(path)
                        path = os.path.join(path, str(FormID))
                        if not os.path.exists(path):
                            os.mkdir(path)
                        file.save(os.path.join(path, filename))
                        contribution.FilePath = os.path.join(path, filename)
                    contribution.StartDate = start_date
                    contribution.EndDate = end_date
                    contribution.LastModifiedDate = initiation_date
                    db.session.commit()
                else:
                    raise Unauthorized()
            elif args["request_type"] == RequestType_ApprovalConfirmation:
                if decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    path = APP.config['DATA_DIR']
                    file = request.files['file']
                    startdate = args["startDate"]
                    enddate = args["endDate"]
                    start_date = datetime.strptime(startdate, "%a %b %d %Y")
                    end_date = datetime.strptime(enddate, "%a %b %d %Y")
                    userid = request.form["employerusername"]
                    if contribution.FilePath is not None:
                        if 'file' in request.files:
                            filename = secure_filename(file.filename)
                            print(filename)
                            path = os.path.join(path, "Employers")
                            if not os.path.exists(path):
                                os.mkdir(path)
                            path = os.path.join(path, userid)
                            if not os.path.exists(path):
                                os.mkdir(path)
                            path = os.path.join(path, "contribution")
                            if not os.path.exists(path):
                                os.mkdir(path)
                            path = os.path.join(path, str(FormID))
                            if not os.path.exists(path):
                                os.mkdir(path)
                            file.save(os.path.join(path, filename))
                            contribution.FilePath = os.path.join(path, filename)
                    contribution.StartDate = start_date
                    contribution.EndDate = end_date
                    contribution.LastModifiedDate = initiation_date
                    contribution.Status = status.STATUS_APPROVE
                    db.session.commit()
                else:
                    raise Unauthorized()
            elif args["request_type"] == RequestType_Reject:
                if decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    contribution.Status = status.STATUS_REJECT
                    if 'Comment' in args and args['Comment'] != '':
                        comment = Comments(
                            FormID=FormID,
                            Name=args['CommentName'],
                            Role=roles.ROLES_EMPLOYER,
                            Comment=args['Comment'],
                            Date=initiation_date,
                        )
                        db.session.add(comment)
                    db.session.commit()
                else:
                    raise Unauthorized()
            elif args["request_type"] == RequestType_Delete:
                if decode_token["role"] == roles.ROLES_REVIEW_MANAGER:
                    file_path = contribution.FilePath
                    if file_path is not None:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        else:
                            raise UnprocessableEntity("Can't find file")
                    else:
                        raise UnprocessableEntity("Can't find filename")
