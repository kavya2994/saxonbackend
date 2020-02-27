import json
import os
import threading
from datetime import datetime
import time

import xlrd
from flask import Blueprint, jsonify, request, send_file
from flask_restx import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from werkzeug.utils import secure_filename

from ...helpers import token_verify_or_raise, RESPONSE_OK, delete_excel
from ...models import db, status, roles
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
parser.add_argument('startDate', type=str, location='form', required=True)
parser.add_argument('endDate', type=str, location='form', required=True)
parser.add_argument('file', type=str, location='form', required=True)

response_model = ns.model('PostInitiateContribution', {
    'error': fields.String,
    'result': fields.String,
})

@ns.route("/initiate")
class InitiateContribution(Resource):
    @ns.doc(description='Generates and Excel sheet of members under employer',
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
        startdate = request.form["startDate"]
        enddate = request.form["endDate"]
        print(startdate)
        start_date = datetime.strptime(startdate, "%a %b %d %Y")
        end_date = datetime.strptime(enddate, "%a %b %d %Y")
        formtype = request.form["formType"]
        userid = request.form["employerusername"]
        employer = request.form["employer"]
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
            contribution = Contributionform(
                FormStatus=status.STATUS_PENDING,
                FormType=formtype,
                InitiatedBy=userid,
                # InitiatedDate=,
                Status=status.STATUS_PENDING,
                PendingFrom=roles.ROLES_REVIEW_MANAGER,
                TokenStatus=status.STATUS_ACTIVE,
                EmployerID=userid,
                LastModifiedDate=datetime.utcnow()
            )
            db.session.add(contribution)
            db.session.commit()

            path = os.path.join(path, str(contribution.FormID))
            if not os.path.exists(path):
                os.mkdir(path)
            file.save(os.path.join(path, filename))
        else:
            return jsonify({"error": "Bad request"}), 400

        return jsonify({"result": "Success"}), 200

