import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restx import Resource, reqparse
from ...helpers import token_verify
from ...models import db
from ...models.terminationform import Terminationform
from ...models.token import Token
from . import ns



parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/send")
class TerminationSend(Resource):
    @ns.doc(parser=parser,
        description='Send Termination',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        member_name = data["membername"]
        member_email = data["email"]
        type = data["request_type"]
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if type == "remainder":
            notify = data["notify"]
            tokenID = data["tokenID"]
            try:
                msg['subject'] = "Please complete your Silver Thatch Pensions Employment Termination Form"
                msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                                   ' Please do not reply to this message. **</p>'
                                   '<p>Dear %s</p>'
                                   '<p>In an effort to keep you connected with your Silver Thatch Pension '
                                   'after you leave your current position, please click here or copy the link '
                                   'below into a browser to complete the termination of employment form. This '
                                   'form notifies us that you are no longer employed with your current '
                                   'employer and allows Silver Thatch Pensions to stay in touch with you in '
                                   'regards to your pension. </p> '
                                   '<p>-----------------------------------------</p>'
                                   '<p>https://183.82.0.186:812/terminationform/%s</p>'
                                   '<p>To learn more about the Silver Thatch Pension Plan,'
                                   ' click here to review our members handbook. </p>' % (member_name, token),
                                   'html')

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
        elif type == "submission_confirmation":
            msg['subject'] = "Your Termination form has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your termination was submitted on %s. '
                               'You will receive notification once your form has been processed</p>' % (
                                   member_name, datetime.utcnow().strftime("%Y-%m-%d")),
                               'html')
            try:
                if not msgtext == "":
                    msg.attach(msgtext)
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200
                else:
                    return "Invalid request", 417
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "approval_confirmation":
            msg['subject'] = "Your Termination has been approved"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your termination has been processed </p>' % (
                                   member_name),
                               'html')
            try:
                if not msgtext == "":
                    msg.attach(msgtext)
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200
                else:
                    return "Invalid request", 417
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "rejected":
            token = data["token"]
            msg['subject'] = "Your termination has been rejected"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Termination has been rejected </p>'
                               '<p>Please click here. Otherwise, cut and paste the link below into a browser, '
                               'fill in the required information, and when you are done hit the submit button to '
                               'start your termination into the plan.</p>'
                               '<p>-----------------------------------------------------</p>'
                               '<p>https://183.82.0.186:812/terminationform/%s </p>'
                               '<p>To learn more about the Silver Thatch Pension '
                               'Plan, click here to review our members handbook. </p>' % (
                                   member_name, token),
                               'html')
            try:
                if not msgtext == "":
                    msg.attach(msgtext)
                    smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                    smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                    return jsonify({"result": "success"}), 200
                else:
                    return "Invalid request", 417
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + str(e))
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500

