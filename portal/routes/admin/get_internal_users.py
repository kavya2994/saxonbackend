import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.users import Users
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)

response_model_child = ns.model('GetGetInternalUsersChild', {
    "Username": fields.String,
    "DisplayName": fields.String,
    "Email": fields.String,
    "Status": fields.String,
    "PhoneNumber": fields.String,
    "Role": fields.String,
})

response_model = ns.model('GetGetInternalUsers', {
    "users": fields.List(fields.Nested(response_model_child))
})


@ns.route("/users/internal/get")
class GetInternalUsers(Resource):
    @ns.doc(description='Get all internal users',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)

        if decoded_token["role"] not in [roles.ROLES_ADMIN]:
            raise Unauthorized()
        try:
            users = Users.query.filter(Users.Role.in_([roles.ROLES_REVIEW_MANAGER, roles.ROLES_ADMIN]),
                                       Users.Status != status.STATUS_DELETE).order_by(
                Users.UserCreatedTime.desc()).all()

            internal_users = []
            for user in users:
                internal_users.append({
                    "Username": user.Username,
                    "DisplayName": user.DisplayName,
                    "Email": user.Email,
                    "Status": user.Status,
                    "PhoneNumber": user.PhoneNumber,
                    "Role": user.Role
                })
            return {"users": internal_users}, 200
        except Exception as e:
            LOG.error("Exception while retrieving internal users", e)
            raise InternalServerError("Can't add employer to user")
