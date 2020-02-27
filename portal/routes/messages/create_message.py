import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.messages import Messages
from werkzeug.exceptions import Unauthorized, BadRequest, UnprocessableEntity, InternalServerError
from . import ns
from ... import APP

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('Subject', type=str, location='json', required=True)
parser.add_argument('Message', type=str, location='json', required=True)
parser.add_argument('AddedBy', type=str, location='json', required=True)

response_model = ns.model('PostCreateMessages', {
    'result': fields.String,
})

@ns.route("/create")
class CreateMessages(Resource):
    @ns.doc(parser=parser,
            description='Get profile details',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        message = args["Message"]
        subject = args["Subject"]
        added_by = args["AddedBy"]
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_REVIEW_MANAGER:
            messages = Messages(
                Message=message,
                Subject=subject,
                AddedBy=added_by,
                CreatedDate=datetime.utcnow()
            )
            db.session.add(messages)
            db.session.commit()

            return {"result": "Success"}, 200
        else:
            raise Unauthorized()
