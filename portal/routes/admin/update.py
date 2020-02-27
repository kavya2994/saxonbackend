from email.mime.text import MIMEText
import json

from flask import Blueprint, jsonify, request, abort, current_app as app, Response
from flask_restx import Resource, reqparse, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise, RESPONSE_OK
from ...encryption import Encryption
from ...models import db, roles
from ...models.users import Users
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)

response_model = ns.model('PostUpdateUser', {
    'result': fields.String,
})

@ns.route("/user/update")
class UpdateUser(Resource):
    @ns.doc(parser=parser,
            description='Update user data',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        data = json.loads(str(request.data, encoding='utf-8'))
        print(data)
        role = data["role"]
        print(role)
        user_name = data["username"]
        print(data["statuschange"])
        user = Users.query.filter_by(Username=user_name).first()
        msgtext = None
        subject = None

        if user is None:
            raise UnprocessableEntity('Username is not valid')
        try:
            if role == roles.ROLES_REVIEW_MANAGER or role == roles.ROLES_ADMIN:

                status_change = data["statuschange"]
                print(status_change)

                if not status_change:

                    display_name = data["displayname"]
                    email = data["email"]
                    phone_number = data["phonenumber"]
                    is_password_change = data["passwordchange"]
                    # session_expiry = data["session_expiry"]

                    if is_password_change:
                        password = randomStringwithDigitsAndSymbols()
                        password_enc = Encryption().encrypt(password)
                        print("password change")
                        user.DisplayName = display_name
                        user.Email = email
                        user.PhoneNumber = phone_number
                        user.Password = password_enc
                        user.TemporaryPassword = True
                        msgtext = MIMEText('<p>Your password has been reset. The temporary password is: %s</p>'
                                           '<p>Please log into your system as soon as possible to set your new password.</p>'
                                           % password, 'html')
                        subject = "Temporary Password for Saxon Portals"

                        # cursor.execute('UPDATE Users set "DisplayName"=\'%s\','
                        #                '"PhoneNumber"=\'%s\',"Email"=\'%s\','
                        #                ' "Password"=\'%s\' WHERE "Username"=\'%s\'' % (
                        #                    display_name, phone_number,
                        #                    email, password, username))
                    else:
                        print("not password change")
                        user.DisplayName = display_name
                        user.Email = email
                        user.PhoneNumber = phone_number

                        # cursor.execute(
                        #     'UPDATE Users set "DisplayName"=\'%s\',"PhoneNumber"=\'%s\',"Email"=\'%s\','
                        #     '"SessionDuration"=\'%s\' WHERE "Username"=\'%s\'' % (display_name, phone_number,
                        #                                                           email, "30",
                        #                                                           username))
                else:
                    status = data["status"]
                    user.Status = str(status).upper()
                #     cursor = conn.cursor()
                #     cursor.execute(
                #         'UPDATE Users set "Status"=\'%s\' WHERE "Username"=\'%s\'' % (status, username))
                # conn.commit()

                db.session.commit()
                if msgtext is not None and subject is not None:
                    send_email(user.Email, subject=subject, body=msgtext)
                return RESPONSE_OK
            elif role == roles.ROLES_EMPLOYER or role == roles.ROLES_MEMBER or role == roles.ROLES_HR:
                display_name = data["displayname"]
                email = data["email"]

                is_password_change = data["passwordchange"]

                # cursor = conn.cursor()
                if is_password_change:
                    password = randomStringwithDigitsAndSymbols()
                    password_enc = Encryption().encrypt(password)
                    user.DisplayName = display_name
                    user.Email = email
                    user.Password = password_enc
                    msgtext = MIMEText('<p>Your password has been reset. The temporary password is: %s</p>'
                                       '<p>Please log into your system as soon as possible to set your new password.</p>'
                                       % password, 'html')
                    subject = "Temporary Password for Saxon Portals"
                    # cursor.execute('UPDATE Users set "DisplayName"=\'%s\',"Email"=\'%s\','
                    #                '"SessionDuration"=\'%s\', "Password"=\'%s\' WHERE "Username"=\'%s\'' % (
                    #                    display_name,
                    #                    email, session_expiry, password, username))
                else:
                    user.DisplayName = display_name
                    user.Email = email
                    # cursor.execute('UPDATE Users set "DisplayName"=\'%s\',"Email"=\'%s\','
                    #                '"SessionDuration"=\'%s\' WHERE "Username"=\'%s\'' % (display_name,
                    #                                                                      email, session_expiry,
                    #                                                                      username))
                    # conn.commit()
                db.session.commit()
                if msgtext is not None and subject is not None:
                    send_email(user.Email, subject=subject, body=msgtext)
                return RESPONSE_OK
            else:
                raise BadRequest('Invalid Role')
        except Exception as e:
            LOG.error("Exception while updating user", e)
            raise InternalServerError("Can't update user")


