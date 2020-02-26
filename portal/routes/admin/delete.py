from flask import Blueprint, jsonify, request, abort, current_app as app, Response
from flask_restplus import Resource, reqparse, fields
from werkzeug.exceptions import UnprocessableEntity, Unauthorized, InternalServerError

from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
from ...models import db, roles, status
from ...models.users import Users
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('user', type=str, location='json', required=True)

response_model = ns.model('PostDeleteUser', {
    "result": fields.String,
    "error": fields.String,
})

# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/user/internal/delete")
class DeleteUser(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='updating user status to deleted',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args(strict=False)
        username = args['username']
        token = args["Authorization"]
        ip = args['Ipaddress']
        decoded_token = token_verify_or_raise(token, username, ip)
        if decoded_token["role"] == roles.ROLES_ADMIN:
            user_id_to_delete = args["user"]
            user = Users.query.filter_by(Username=user_id_to_delete).first()
            role = user.Role
            try:
                if not user.Role == roles.ROLES_EMPLOYER and not user.Role == roles.ROLES_MEMBER:
                    user.Status = status.STATUS_DELETE
                    db.session.commit()
                    return {"result": "User Deleted successfully"}, 200
                else:
                    return {"error": "Can't Delete " + user.Role}, 500
            except Exception as e:
                LOG.error("Exception while deleting ", e)
                raise InternalServerError("Can't delete user" + user_id_to_delete)
        else:
            raise Unauthorized()




