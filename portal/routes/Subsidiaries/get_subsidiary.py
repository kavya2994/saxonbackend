import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app

from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status
from ...models.roles import *
from ...models.subsidiaries import Subsidiaries
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('employer_id', type=str, location='json', required=True)

response_model_child = ns.model('GetSubsidiaryChild', {
    'EmployerID': fields.String,
    'EmployerName': fields.String,
    'SubsidiaryID': fields.String,
    'SubsidiaryName': fields.String
})

response_model = ns.model('GetSubsidiary', {
    'subsidiaries': fields.List(fields.Nested(response_model_child))
})


@ns.route("/get")
class GetSubsidiary(Resource):
    @ns.doc(description='Get subsidiaries',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        try:
            username = args['username']
            token = args["Authorization"]
            ip = args['Ipaddress']
            employer_id = args["employer_id"]
            decoded_token = token_verify_or_raise(token, username, ip)
            # print(decoded_token)
            if decoded_token["role"] in [ROLES_REVIEW_MANAGER, ROLES_EMPLOYER, ROLES_ADMIN]:

                subsidiaries = Subsidiaries.query.filter_by(EmployerID=employer_id).all()
                subsidiaries_list = []
                for subsidiary in subsidiaries:
                    subsidiaries_list.append({
                        'EmployerID': subsidiary.EmployerID,
                        'EmployerName': subsidiary.EmployerName,
                        'SubsidiaryID': subsidiary.SubsidiaryID,
                        'SubsidiaryName': subsidiary.SubsidiaryName
                    })

                return {'subsidiaries': subsidiaries_list}, 200
            else:
                raise Unauthorized()
        except Exception as e:
            LOG.error("Exception while fetching subsidiaries", e)
            raise InternalServerError("Can't fetch subsidiaries")
