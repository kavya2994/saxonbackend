from flask import Blueprint, request, abort, current_app as app
from flask_restplus import Resource, reqparse, fields
from ...helpers import randomStringwithDigitsAndSymbols, token_verify, token_verify_or_raise, crossdomain
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
parser.add_argument('SubsidiaryName', type=str, location='json', required=True)
parser.add_argument('EmployerID', type=str, location='json', required=True)
parser.add_argument('EmployerName', type=str, location='json', required=True)

response_model = ns.model('PostAddSubsidiary', {
    'result': fields.String,
})

# @user_blueprint.route('/createuser', methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'Ipaddress', 'User'])
@ns.route("/add")
class AddSubsidiary(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Add new subsidiary',
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
            new_subsidiary = Subsidiaries(
                                EmployerID=args["EmployerID"],
                                EmployerName=args["EmployerName"],
                                SubsidiaryID=args["SubsidiaryID"],
                                SubsidiaryName=args["SubsidiaryName"])
            db.session.add(new_subsidiary)
            db.session.commit()

            return {"result": "Subsidiary added successfully"}, 200
        except Exception as e:
            LOG.error("Exception while adding new subsidiary", e)
            raise InternalServerError("Can't add subsidiary")
