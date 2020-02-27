import jwt
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, abort, current_app as app
from flask_restx import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status, roles
from ...models.users import Users
from ...services.mail import send_email
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...models.security_question import SecurityQuestion
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)

response_model = ns.model('PostAddUser', {
    'result': fields.String,
})

@ns.route("/createuser")
class AddUser(Resource):
    @ns.doc(parser=parser,
            description='Create New User',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        if token["role"] == roles.ROLES_ADMIN:
            data = json.loads(str(request.data, encoding='utf-8'))
            print(data)
            username = data["username"]
            displayname = data["displayname"]
            email = data["email"]
            # session_duration = data["SessionDuration"]
            password = randomStringwithDigitsAndSymbols(10)
            enc_pass = Encryption().encrypt(password)
            userexist = Users.query.filter_by(Username=username).first()
            try:
                if userexist is None:
                    new_user = Users(Username=username,
                                     Email=email,
                                     Password=enc_pass,
                                     Role=data["role"],
                                     Status=status.STATUS_ACTIVE,
                                     TemporaryPassword=True,
                                     DisplayName=displayname,
                                     SessionDuration="30",
                                     UserCreatedTime=datetime.utcnow())
                    db.session.add(new_user)
                    db.session.commit()
                    msg_text = f'<p>Dear {displayname}</p>' + \
                                f'<p>Your account has been reactivated</p>' + \
                                f'<p>Username is {username}</p>' + \
                                f'<p> please use this password {password} to log in</p>'

                    send_email(email, "Welcome to Pension Management portal", body=msg_text)
                    return {"result": "Success"}, 200
                elif userexist.Status == status.STATUS_DELETE:
                    userexist.Username = username
                    userexist.Email = email
                    userexist.Password = enc_pass
                    userexist.Role = data["role"]
                    userexist.Status = status.STATUS_ACTIVE
                    userexist.TemporaryPassword = True
                    userexist.DisplayName = displayname
                    userexist.SessionDuration = "30"
                    userexist.UserCreatedTime = datetime.utcnow()
                    db.session.commit()
                    msg_text = f'<p>Dear {displayname}</p>' + \
                                f'<p>Your account is created</p>' + \
                                f'<p>Username is {username}</p>' + \
                                f'<p> please use this password {password} to log in</p>'

                    send_email(email, "Welcome to Pension Management portal", body=msg_text)

                    return {"result": "Success"}, 200
                else:
                    raise UnprocessableEntity('Duplicate user cannot be created')
            except Exception as e:
                LOG.error("Exception while adding new user", e)
                raise InternalServerError("Can't add user")
        else:
            raise Unauthorized('You have No Authorization')

