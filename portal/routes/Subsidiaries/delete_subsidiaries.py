import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse
from ...helpers import token_verify_or_raise, crossdomain

from ...models import db, status, roles
from ...models.subsidiaries import Subsidiaries
from werkzeug.exceptions import UnprocessableEntity, Unauthorized
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('SubsidiaryID', type=str, location='json', required=True)
parser.add_argument('EmployerID', type=str, location='json', required=True)


@ns.route("/delete")
class DeleteSubsidiary(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description=' Delete subsidiary',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["Role"] == roles.ROLES_ADMIN:
            subsidiaries = Subsidiaries.query.filter_by(EmployerID=args["EmployerID"],
                                                        SubsidiaryID=args["SubsidiaryID"]).first()
            if subsidiaries is not None:
                subsidiaries.delete()
                db.session.commit()
            else:
                raise UnprocessableEntity('Cant find the subsidiary')
        else:
            raise Unauthorized()
