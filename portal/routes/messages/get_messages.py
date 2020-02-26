import jwt
import json
from datetime import datetime
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
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


messages_model = ns.model('GetGetMessagesMessage', {
    'Subject': fields.String,
    'Message': fields.String,
    'CreatedDate': fields.DateTime,
    'MessageID': fields.Integer
})

response_model = ns.model('GetGetMessages', {
    "messages": fields.List(fields.Nested(messages_model))
})


@ns.route("/get")
class GetMessages(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get profile details',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] in [roles.ROLES_REVIEW_MANAGER, roles.ROLES_MEMBER, roles.ROLES_EMPLOYER]:
            messages = Messages.query.all()
            messages_list = []
            for message in messages:
                messages_list.append({
                    "Message": message.Message,
                    "Subject": message.Subject,
                    "CreatedDate": message.CreatedDate,
                    "MessageID": message.MessageID
                })
            return {"messages": messages_list}, 200
        else:
            raise Unauthorized()

