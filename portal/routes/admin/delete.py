from flask import Blueprint, jsonify, request, abort, current_app as app, Response
from flask_restplus import Resource, reqparse
from werkzeug.exceptions import UnprocessableEntity, Unauthorized

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise
from ...models import db, roles, status
from ...models.users import Users
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='json', required=True)


# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/user/internal/delete")
class DeleteUser(Resource):
    @ns.doc(parser=parser,
            description='Update user data',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['Username']
        token = args["Authorization"]
        ip = args['IpAddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["Role"] == roles.ROLES_ADMIN:
            user_id_to_delete = args["username"]
            user = Users.query.filter_by(Username=user_id_to_delete).first()
            role = user.Role
            if not user.Role == roles.ROLES_EMPLOYER and not user.Role == roles.ROLES_MEMBER:
                user.Status = status.STATUS_DELETE
                db.session.commit()
                return {"result": "User Deleted successfully"}, 200
            else:
                return {"error": "Can't Delete " + user.Role}, 500
        else:
            raise Unauthorized()




