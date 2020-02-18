import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, abort
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import randomStringwithDigitsAndSymbols, token_verify_or_raise
from ...encryption import Encryption
from ...models import db, status
from ...models.users import Users
from ...models.security_question import SecurityQuestion
from ...models.terminationform import Terminationform
from ...models.token import Token
from . import ns

parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)

TerminationformResponseModel = {
    "EmployerName": fields.String,
    "FormType": fields.String,
    "FormStatus": fields.String,
    "LastModifiedDate": fields.date_from_iso8601
}
# parser.add_argument('memberid', type=str, location='json', required=True)


@ns.route("/terminationdetails")
class MemberTerminationDetails(Resource):
    @ns.doc(parser=parser,
            description='Get member termination details ',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 422: 'UnprocessableEntity',
                       500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(TerminationformResponseModel)
    def get(self):
        args = parser.parse_args(strict=False)
        token = token_verify_or_raise(token=args["Authorization"], ip=args["Ipaddress"], user=args["username"])

        # TODO:
        # Verify the role from token before proceeding with password chanaging
        # Employer name ,form type, status , last modified date

        terminations_list = []
        username = args["username"]
        print(username)
        tokens = db.session.query(Token, Terminationform).filter(Token.FormID == Terminationform.FormID,
                                                                 Terminationform.MemberNumber == str(username),
                                                                 Token.FormType == "Termination",
                                                                 Token.FormStatus == status.STATUS_APPROVE,
                                                                 Token.TokenStatus == status.STATUS_INACTIVE).all()
        # terminations = Terminationform.query.filter_by(MemberNumber='25360').all()
        # for termination in terminations:
        #     print(termination.FormStatus)
        for token_data, termination in tokens:
            print(token_data.__dict__)
            print(termination.__dict__)
            terminations_list.append({
                "EmployerName": termination.EmployerName,
                "FormType": token_data.FormType,
                "FormStatus": token_data.FormStatus,
                "LastModifiedDate": token_data.LastModifiedDate
            })
        return {"TerminationForms": terminations_list}, 200

