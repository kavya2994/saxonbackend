import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from werkzeug.exceptions import NotFound, BadRequest, UnprocessableEntity, InternalServerError
from ...helpers import token_verify
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('Username', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)

parser.add_argument('Name', type=str, location='json', required=True)
parser.add_argument('Email', type=str, location='json', required=True)
parser.add_argument('RequestType', type=str, location='json', required=True)
parser.add_argument('Notify', type=bool, location='json', required=False)

# Remainder
# ApprovalConfirmation
# Rejected

@ns.route('/send')
class EnrollmentFile(Resource):
    @ns.doc(parser=parser,
        description='Send Enrollment Form',
        responses={
            200: 'OK',
            400: 'Bad Request',
            401: 'Unauthorized',
            500: 'Internal Server Error'
        })

    @ns.expect(parser, validate=True)
    def post(self):
        args = parser.parse_args(strict=True)
        # if args['RequestType'] == 'Remainder'


    def _original(self):
        token_id = request.args["TokenID"]
        print(request.get_data())
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        print(data)
        member_name = data["membername"]
        member_email = data["email"]
        request_type = data["request_type"]
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if request_type == "remainder":
            notify = data["notify"]
            try:
                token_data = Token.query.get(token_id)
                form_data = Enrollmentform.query.filter_by(tokenID=token_data["TokenID"]).first()
                if "formCreatedDate" in form_data.keys():
                    # init_time = datetime.strptime(form_data["formCreatedDate"], "%d%m%Y %H:%M:%S.%f")
                    # time = (datetime.utcnow() - form_data["formCreatedDate"]).days
                    msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                                       ' Please do not reply to this message. **</p>'
                                       '<p>Dear %s</p>'
                                       '<p>Please click here. Otherwise, '
                                       'cut and paste the link below into a browser, fill in the '
                                       'required information, and when you are done'
                                       ' hit the submit button to start your enrollment '
                                       'into the plan.</p>'
                                       '<p>-----------------------------------------</p>'
                                       '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
                                       '<p>To learn more about the Silver Thatch Pension Plan,'
                                       ' click here to review our members handbook. </p>' % (member_name, token),
                                       'html')
                    # if time == 3:
                    #     notify = True
                    # elif time > 3:
                    #     if "notifytime" in form_data:
                    #         # notify_time = datetime.strptime(form_data["notifytime"], "%d%m%Y %H:%M:%S.%f")
                    #         time_days = (datetime.utcnow() - form_data["notifytime"]).days
                    #         if time_days == 3:
                    #             notify = True
                    if notify:
                        msg.attach(msgtext)
                        smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                        smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                        return jsonify({"result": "success"}), 200

            except KeyError as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened"}), 500

        elif request_type == "approval_confirmation":
            msg['subject'] = "Your Enrollment has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment has been processed </p>' % (
                                   member_name),
                               'html')

            tkn = Token.query.get(token_id)
            tkn.status = "approved"
            db.session.commit()

            try:
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500

        elif request_type == "rejected":
            msg['subject'] = "Your Enrollment has been rejected"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment has been rejected </p>'
                               '<p>Please click here. Otherwise, cut and paste the link below into a browser, '
                               'fill in the required information, and when you are done hit the submit button to '
                               'start your enrollment into the plan.</p>'
                               '<p>%s</p>'
                               '<p>-----------------------------------</p>'
                               '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
                               '<p>To learn more about the Silver Thatch Pension '
                               'Plan, click here to review our members handbook. </p>' % (
                                   member_name, data["comments"], token),
                               'html')
            try:
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
