import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, cors, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ....helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise
from ....encryption import Encryption
from ....models import db
from ....models.users import Users
from ....models.security_question import SecurityQuestion
from .. import ns
from .... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('user', type=str, location='json', required=True)
parser.add_argument('oldPassword', type=str, location='json', required=True)
parser.add_argument('newPassword', type=str, location='json', required=True)

response_model = ns.model('PostPasswordChange', {
    'result': fields.String,
})

@ns.route("/password/change")
class PasswordChange(Resource):
    @ns.doc(description='Change Password',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 422: 'UnprocessableEntity',
                       500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        # TODO:
        # Verify the role from token before proceeding with password chanaging

        username = args["user"]
        old_pass = args["oldPassword"]
        new_pass = args["newPassword"]

        user = Users.query.filter_by(Username=username).first()
        if user is None:
            raise UnprocessableEntity('Username is not valid')

        if user.Password != Encryption().encrypt(old_pass):
            raise BadRequest('Old Password is wrong')

        try:
            decrypted = None
            decrypted_list = []
            last5 = ""
            if user.Last5Passwords is not None and user.Last5Passwords != "":
                print(user.Last5Passwords)
                try:
                    decrypted = Encryption().decrypt(user.Last5Passwords)
                except Exception as e:
                    print(e)
                    LOG.error(e)
                if decrypted is not None:
                    decrypted_list = decrypted.split("/,deli#@./")
                    if new_pass in decrypted_list:
                        raise UnprocessableEntity("This password was used recently (one of the last 5). Please try "
                                                  "another.")
            decrypted_list.append(new_pass)
            print(decrypted_list)
            if len(decrypted_list) >= 5:
                for i in range(len(decrypted_list) - 5):
                    decrypted_list.remove(decrypted_list[0])

            for i in decrypted_list:
                if i is not None:
                    if not decrypted_list.index(i) == len(decrypted_list) - 1:
                        last5 += str(i) + "/,deli#@./"
                    else:
                        last5 += str(i)
            print(last5)
            if not last5 == "":
                user.Last5Passwords = Encryption().encrypt(last5)
                user.PassLastUpdatedDate = datetime.utcnow()
            user.Password = Encryption().encrypt(new_pass)
            user.TemporaryPassword = False
            db.session.commit()
            return {"result": "Password changed successfully"}, 200

        except KeyError as e:
            print(e)
            raise InternalServerError()
