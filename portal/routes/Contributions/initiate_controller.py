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
parser.add_argument('employerusername', type=str, location='form', required=True)
parser.add_argument('employername', type=str, location='form', required=True)
parser.add_argument('startDate', type=str, location='form', required=True)
parser.add_argument('endDate', type=str, location='form', required=True)
parser.add_argument('Comment', type=str, location='form', required=False)
parser.add_argument('file', type=FileStorage, location='files', required=True)

response_model = ns.model('PostInitiateContribution', {
    'error': fields.String,
    'result': fields.String,
})


@ns.route("/initiate")
class InitiateContribution(Resource):
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
        startdate = args["startDate"]
        enddate = args["endDate"]
        print(startdate)
        print(enddate)
        initiation_date = datetime.utcnow()
        start_date = datetime.strptime(startdate, "%a %b %d %Y")
        end_date = datetime.strptime(enddate, "%a %b %d %Y")
        userid = request.form["employerusername"]
        employer_name = request.form["employername"]
        path = os.path.join(path, "Employers")
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, userid)
        if not os.path.exists(path):
            os.mkdir(path)
        path = os.path.join(path, "contribution")
        if not os.path.exists(path):
            os.mkdir(path)
        if 'file' in request.files:
            filename = secure_filename(file.filename)
            print(filename)
            try:
                contribution = Contributionform(
                    StartDate=start_date,
                    EndDate=end_date,
                    Status=status.STATUS_PENDING,
                    PendingFrom=roles.ROLES_REVIEW_MANAGER,
                    EmployerName=employer_name,
                    Date=initiation_date,
                    EmployerID=userid,
                    LastModifiedDate=initiation_date
                )
                db.session.add(contribution)
                db.session.commit()
                if 'Comment' in args and args['Comment'] != '' and args['Comment'] is not None:
                    comment = Comments(
                        FormID=contribution.FormID,
                        Name=employer_name,
                        Role=decode_token['role'],
                        Comment=args['Comment'],
                        Date=initiation_date,
                        FormType="Contribution"
                    )
                    db.session.add(comment)
                    db.session.commit()

                path = os.path.join(path, str(contribution.FormID))
                if not os.path.exists(path):
                    os.mkdir(path)
                file.save(os.path.join(path, filename))
                contribution.FilePath = os.path.join(path, filename)
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

