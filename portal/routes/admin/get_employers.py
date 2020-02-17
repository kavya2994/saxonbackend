import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.employer_view import EmployerView
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
# parser.add_argument('min', type=str, location='json', required=True)
# parser.add_argument('max', type=str, location='json', required=True)

response_model = {
    'ERKEY': fields.String,
    'ERNO': fields.String,
    'ENAME': fields.String,
    'SNAME': fields.String,
    'EMAIL': fields.String
}


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/employers/get")
class GetEmployers(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get all employers in b/w min and max',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        # minimum = args["min"]
        # maximum = args["max"]
        decoded_token = token_verify_or_raise(token, username, ip)

        if decoded_token["role"] == roles.ROLES_ADMIN:
            employers = EmployerView.query.all()#limit(minimum).offset(maximum)
            employer_list = []
            for emp in employers:
                employer_list.append({
                    'ERKEY': emp.ERKEY,
                    'ERNO': emp.ERNO,
                    'ENAME': emp.ENAME,
                    'SNAME': emp.SNAME,
                    'EMAIL': emp.EMAIL
                })
            return {"employers": employer_list}, 200
        else:
            raise Unauthorized()
