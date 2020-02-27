import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from ...helpers import token_verify_or_raise

from ...models import db, status, roles
from ...models.subsidiaries import Subsidiaries
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('SubsidiaryID', type=str, location='json', required=True)
parser.add_argument('EmployerID', type=str, location='json', required=True)


response_model = ns.model('PostDeleteSubsidiary', {
    'result': fields.String,
})

@ns.route("/delete")
class DeleteSubsidiary(Resource):
    @ns.doc(parser=parser,
            description=' Delete subsidiary',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)

        if decoded_token["role"] not in [roles.ROLES_ADMIN]:
            raise Unauthorized()
        try:
            Subsidiaries.query.filter_by(EmployerID=args["EmployerID"],
                                         SubsidiaryID=args["SubsidiaryID"]).delete()

            db.session.commit()
            return {"result": "Success"}, 200
        except Exception as e:
            LOG.error('Exception while deleting susbsidiaryid %s employerid %s %s' % (
                args["SubsidiaryID"], args["EmployerID"], e))
            raise InternalServerError()
        # else:
        #     raise UnprocessableEntity('Cant find the subsidiary')
