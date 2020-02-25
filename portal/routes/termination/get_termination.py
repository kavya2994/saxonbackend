import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, inputs, fields
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, UnprocessableEntity, InternalServerError
from ...helpers import token_verify_or_raise, crossdomain, RESPONSE_OK
from ...models import db, status, roles
from ...models.terminationform import Terminationform, TerminationformResponseModel
from ...models.token import Token, TOKEN_FORMTYPE_TERMINATION
from ...models.comments import Comments
from ...models.roles import *
from ...services.mail import send_email
from . import ns
from ... import APP, LOG

parser = reqparse.RequestParser()
# parser.add_argument('Authorization', type=str, location='headers', required=True)
# parser.add_argument('username', type=str, location='headers', required=True)
# parser.add_argument('Ipaddress', type=str, location='headers', required=True)

comments_response = {
    "Name": fields.String,
    "Date": fields.String,
    "Comment": fields.String,

}
response_model = {
    "EmployerName": fields.String,
    "EmployerID": fields.String,
    "InitiatedDate": fields.DateTime,
    "MemberName": fields.String,
    "MemberNumber": fields.String,
    "EmailAddress": fields.String,
    "FinalDateOfEmployment": fields.DateTime,
    "ReasonforTermination": fields.String,
    "LastDeduction": fields.String,
    "Address": fields.String,
    "AddressLine2": fields.String,
    "District": fields.String,
    "PostalCode": fields.String,
    "Country": fields.String,
    "EstimatedAnnualIncomeRange": fields.String,
    "Status": fields.String,
    "PendingFrom": fields.String,
    "PhoneNumber": fields.String,
    "Comment": fields.List(fields.Nested(comments_response))
}


@ns.route("/get/<TokenID>")
class GetTermination(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    @ns.doc(parser=parser,
            description='Get The termination form data',
            responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    @ns.expect(parser, validate=True)
    @ns.marshal_with(response_model)
    def get(self, TokenID):
        args = parser.parse_args()
        print(TokenID)
        # decode_token = token_verify_or_raise(token=args['Authorization'], ip=args['Ipaddress'], user=args['username'])
        token_data = Token.query.filter_by(TokenID=TokenID).first()
        if token_data is not None and token_data.TokenStatus == status.STATUS_ACTIVE:
            termination_form = Terminationform.query.filter_by(FormID=token_data.FormID).first()
            comments = Comments.query.filter(Comments.FormID == token_data.FormID).order_by(Comments.CommentsID.desc()).all()
            comments_list =[]
            if termination_form is not None:
                if comments is not None:
                    for comment in comments:
                        comments_list.append({
                            "Name": comment.Name,
                            "Date": comment.Date,
                            "Comment": comment.Comment
                        })

                return {
                    "EmployerName": termination_form.EmployerName,
                    "EmployerID": termination_form.EmployerID,
                    "InitiatedDate": termination_form.InitiatedDate,
                    "MemberName": termination_form.MemberName,
                    "MemberNumber": termination_form.MemberNumber,
                    "EmailAddress": termination_form.EmailAddress,
                    "FinalDateOfEmployment": termination_form.FinalDateOfEmployment,
                    "ReasonforTermination": termination_form.ReasonforTermination,
                    "LastDeduction": termination_form.LastDeduction,
                    "Address": termination_form.Address,
                    "AddressLine2": termination_form.AddressLine2,
                    "District": termination_form.District,
                    "PostalCode": termination_form.PostalCode,
                    "Country": termination_form.Country,
                    "EstimatedAnnualIncomeRange": termination_form.EstimatedAnnualIncomeRange,
                    "Status": termination_form.Status,
                    "PendingFrom": termination_form.PendingFrom,
                    "PhoneNumber": termination_form.PhoneNumber,
                    "Comment": comments_list
                }, 200
        else:
            raise UnprocessableEntity('Invalid token')
