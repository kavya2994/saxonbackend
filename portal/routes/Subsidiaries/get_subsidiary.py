import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app

from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.subsidiaries import Subsidiaries
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('employer_id', type=str, location='json', required=True)

response_model = {
    'EmployerID': fields.String,
    'EmployerName': fields.String,
    'SubsidiaryID': fields.String,
    'SubsidiaryName': fields.String

}

response = {
    'subsidiaries': fields.List(fields.Nested(response_model))
}


@ns.route("/get")
class GetSubsidiary(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get subsidiaries',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response)
    def post(self):
        args = parser.parse_args(strict=False)
        try:
            username = args['username']
            token = args["Authorization"]
            ip = args['Ipaddress']
            employer_id = args["employer_id"]
            decoded_token = token_verify_or_raise(token, username, ip)
            # print(decoded_token)
            if decoded_token["role"] == roles.ROLES_ADMIN or decoded_token["role"] == roles.ROLES_REVIEW_MANAGER:

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
