import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from flask_restplus import Resource, reqparse
from ...helpers import token_verify
from ...models import db
from ...models.terminationform import Terminationform
from ...models.token import Token
from . import ns



parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('User', type=str, location='headers', required=True)
parser.add_argument('IpAddress', type=str, location='headers', required=True)


@ns.route("/initiate")
class TerminationInitiate(Resource):
    @ns.doc(parser=parser,
        description='Initiate Termination',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def post(self):
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                auth1 = request.headers["Authorization"]
                auth1 = jwt.decode(auth1, key='secret')
                if auth1["role"] == "employer":
                    data = json.loads(str(request.get_data(), encoding='utf-8'))
                    # member_email = data["email"]
                    # employer_id = data["id"]
                    # member_name = data["membername"]
                    # employer_comments = data["comments"]
                    member_email = data["email"]
                    employer_id = data["employernumber"]
                    employer_name = data["employername"]
                    member_name = data["memberfirstName"]
                    form_type = data["formType"]
                    employer_comments = data["comments"]
                    employernumber = employer_id
                    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
                    msg = MIMEMultipart()
                    msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg['from'] = "venkatesh"
                    msg['to'] = member_name

                    try:
                        data["formCreatedDate"] = datetime.utcnow()
                        if str(employer_id)[-2:].__contains__("HR"):
                            employernumber = str(employer_id)[:-2]
                        print(employernumber)

                        myform_enroll = Terminationform()
                        for column_name in [column.key for column in Terminationform.__table__.columns]:
                            if column_name in data:
                                myform_enroll[column_name] = data[column_name]
                        db.session.add(myform_enroll)
                        db.session.commit()

                        token_data = Token(
                            FormID=column_name.id,
                            FormCreatedDate=datetime.utcnow(),
                            FormStatus="pending",
                            FormType="termination",
                            InitiatedBy=employer_id,
                            # InitiatedDate=,
                            PendingFrom="member",
                            TokenStatus="active",
                            EmployerID=employernumber,
                            # OlderTokenID=,
                        )

                        db.session.add(token_data)
                        db.session.commit()

                        token = token_data.TokenID
                        msgtext = MIMEText(
                            '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>'
                            '<p>Dear %s</p>'
                            '<p>In an effort to keep you connected with your Silver Thatch Pension after you leave your '
                            'current position, please click here or copy the link below into a browser to complete the '
                            'termination of employment form. This form notifies us that you are no longer employed with '
                            'your current employer and allows Silver Thatch Pensions to stay in touch with you in regards '
                            'to your pension. </p><p>-----------------------------------------</p> '
                            '<p>https://183.82.0.186:812/terminationform/%s</p>'
                            '<p>To learn more about the Silver Thatch Pension Plan,'
                            ' click here to review our members handbook. </p>' % (member_name, token), 'html')
                        msg.attach(msgtext)
                        smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                        smtpObj.set_debuglevel(2)
                        smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                        return jsonify({"result": "Success"}), 200
                    except Exception as e:
                        print(str(e))
                        file = open("log.txt", "a+")
                        file.writelines(str(datetime.utcnow()) + str(e))
                        file.close()
                        return jsonify({"error": "Something wrong happened"}), 500
            except Exception as e:
                print(str(e))
                return {"error": "Unauthorized"}, 401
