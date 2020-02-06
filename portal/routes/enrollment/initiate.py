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
from werkzeug.utils import secure_filename
from ...helpers import token_verify
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns

initiate_parser = reqparse.RequestParser()
initiate_parser.add_argument('Authorization', type=str, location='headers', required=True)
initiate_parser.add_argument('User', type=str, location='headers', required=True)
initiate_parser.add_argument('IpAddress', type=str, location='headers', required=True)
initiate_parser.add_argument('Password', type=str, location='json', required=True)
initiate_parser.add_argument('IP', type=str, location='json', required=False)
initiate_parser.add_argument('email', type=str, location='json', required=False)
initiate_parser.add_argument('employernumber', type=str, location='json', required=False)
initiate_parser.add_argument('memberfirstName', type=str, location='json', required=False)
initiate_parser.add_argument('comments', type=str, location='json', required=False)
initiate_parser.add_argument('formCreatedDate', type=str, location='json', required=False)
initiate_parser.add_argument('EmployerName', type=str, location='json', required=False)
initiate_parser.add_argument('EmployerID', type=str, location='json', required=False)
initiate_parser.add_argument('InitiatedDate', type=str, location='json', required=False)
initiate_parser.add_argument('AlreadyEnrolled', type=str, location='json', required=False)
initiate_parser.add_argument('Status', type=str, location='json', required=False)
initiate_parser.add_argument('FirstName', type=str, location='json', required=False)
initiate_parser.add_argument('MiddleName', type=str, location='json', required=False)
initiate_parser.add_argument('LastName', type=str, location='json', required=False)
initiate_parser.add_argument('DOB', type=str, location='json', required=False)
initiate_parser.add_argument('Title', type=str, location='json', required=False)
initiate_parser.add_argument('MaritalStatus', type=str, location='json', required=False)
initiate_parser.add_argument('MailingAddress', type=str, location='json', required=False)
initiate_parser.add_argument('AddressLine2', type=str, location='json', required=False)
initiate_parser.add_argument('District', type=str, location='json', required=False)
initiate_parser.add_argument('PostalCode', type=str, location='json', required=False)
initiate_parser.add_argument('Country', type=str, location='json', required=False)
initiate_parser.add_argument('EmailAddress', type=str, location='json', required=False)
initiate_parser.add_argument('Telephone', type=str, location='json', required=False)
initiate_parser.add_argument('StartDateofContribution', type=str, location='json', required=False)
initiate_parser.add_argument('StartDateofEmployment', type=str, location='json', required=False)
initiate_parser.add_argument('ConfirmationStatus', type=str, location='json', required=False)
initiate_parser.add_argument('SignersName', type=str, location='json', required=False)
initiate_parser.add_argument('Signature', type=str, location='json', required=False)
initiate_parser.add_argument('Estimatedannualincomerange', type=str, location='json', required=False)
initiate_parser.add_argument('ImmigrationStatus', type=str, location='json', required=False)
initiate_parser.add_argument('PendingFrom', type=str, location='json', required=False)
initiate_parser.add_argument('SpouseName', type=str, location='json', required=False)
initiate_parser.add_argument('SpouseDOB', type=str, location='json', required=False)

@ns.route("/initiate")
class EnrollmentInitiation(Resource):
    @ns.doc(parser=initiate_parser,
        description='Enrollment Initiation',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(initiate_parser, validate=True)
    def post(self):
        args = initiate_parser.parse_args()
        print(request.headers)
        if not token_verify(token=args["Authorization"], ip=args["IpAddress"], user=args["User"]):
            print("role is not employer")
            return "Unauthorized", 401

        try:
            auth = args["Authorization"]
            auth = jwt.decode(auth, key='secret')
            if auth["role"] != "employer":
                print("role is not employer")
                return "Unauthorized", 401

            member_email = args["email"]
            employer_id = args["employernumber"]
            member_name = args["memberfirstName"]
            employer_comments = args["comments"]
            print(data)

            smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
            msg = MIMEMultipart()
            msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
            msg['from'] = "venkatesh"
            msg['to'] = member_name
            employernumber = employer_id

            try:
                args["formCreatedDate"] = datetime.utcnow()
                if str(employer_id)[-2:].__contains__("HR"):
                    employernumber = str(employer_id)[:-2]
                print(employernumber)

                new_enrollment = Enrollmentform(
                    EmployerName=args["EmployerName"],
                    EmployerID=args["EmployerID"],
                    InitiatedDate=args["InitiatedDate"],
                    AlreadyEnrolled=args["AlreadyEnrolled"],
                    Status=args["Status"],
                    FirstName=args["FirstName"],
                    MiddleName=args["MiddleName"],
                    LastName=args["LastName"],
                    DOB=args["DOB"],
                    Title=args["Title"],
                    MaritalStatus=args["MaritalStatus"],
                    MailingAddress=args["MailingAddress"],
                    AddressLine2=args["AddressLine2"],
                    District=args["District"],
                    PostalCode=args["PostalCode"],
                    Country=args["Country"],
                    EmailAddress=args["EmailAddress"],
                    Telephone=args["Telephone"],
                    StartDateofContribution=args["StartDateofContribution"],
                    StartDateofEmployment=args["StartDateofEmployment"],
                    ConfirmationStatus=args["ConfirmationStatus"],
                    SignersName=args["SignersName"],
                    Signature=args["Signature"],
                    Estimatedannualincomerange=args["Estimatedannualincomerange"],
                    ImmigrationStatus=args["ImmigrationStatus"],
                    pendingFrom=args["PendingFrom"],
                    SpouseName=args["SpouseName"],
                    SpouseDOB=args["SpouseDOB"],
                )

                db.session.add(new_enrollment)
                db.session.commit()

                token_data = Token(
                    FormID=new_enrollment.id,
                    FormCreatedDate=datetime.utcnow(),
                    FormStatus="pending",
                    FormType="Enrollment",
                    InitiatedBy=employer_id,
                    # InitiatedDate=
                    PendingFrom="member",
                    TokenStatus="active",
                    EmployerID=employernumber,
                    # OlderTokenID=
                )

                db.session.add(token_data)
                db.session.commit()

                token = token_data.TokenID
                msgtext = MIMEText(
                    '<p>**This is an auto-generated e-mail message. Please do not reply to this message. **</p>'
                    '<p>Dear %s</p>'
                    '<p>Please click here. Otherwise, cut and paste the link below into a browser, fill in the '
                    'required information, and when you are done hit the submit button to start your enrollment '
                    'into the plan.</p><p>-----------------------------------------</p>'
                    '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
                    '<p>To learn more about the Silver Thatch Pension Plan,'
                    ' click here to review our members handbook. </p>' % (member_name, token), 'html')
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return {"result": "Success"}, 200
            except Exception as e:
                return "Something wrong happened", 500

        except Exception as e:
            print(str(e))
            return "Unauthorized", 401


# @enrollment_blueprint.route("/delete_enrollment_file", methods=['POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
# @ns.route("/delete")
# def deleteenrollmentfile():
#     if request.method == "POST":
#         base_path = os.path.join(app.config['DATA_DIR'], 'Employers')
#         data = json.loads(str(request.get_data(), encoding='utf-8'))
#         employer = data["employerid"]
#         path = data["path"]
#         base_path = os.path.join(base_path, employer, path)
#         if os.path.exists(base_path) and os.path.isfile(base_path):
#             try:
#                 os.remove(base_path)
#                 return jsonify({"result": "success"}), 200
#             except Exception as e:
#                 print(str(e))
#                 return jsonify({"error": "Can't delete the file"}), 500
#         else:
#             return jsonify({"error": "Bad request"}), 400


# @enrollment_blueprint.route("/save_enrollment", methods=['GET', 'POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
# def save_enrollment():
#     if request.method == "POST":
#         member_name = request.form.get("membername")
#         tokenID = request.form.get("tokenID")
#         member_email = request.form.get("email")
#         request_type = request.form.get("request_type")
#         employer_id = request.form.get("employerusername")
#         path = app.config['DATA_DIR']
#         msgtext = ""
#         msg = MIMEMultipart()
#         msg['from'] = "venkatesh"
#         msg['to'] = member_name
#         smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
#         token_data = Token.query.get(tokenID)

#         if request_type == "member_submission":
#             msg['subject'] = "Your Enrollment has been submitted"
#             msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
#                                ' Please do not reply to this message. **</p>'
#                                '<p>Dear %s</p>'
#                                '<p>Your Enrollment was submitted on %s. '
#                                'You will receive notification once your form has been processed</p>' % (
#                                    member_name, datetime.utcnow().strftime("%Y-%m-%d")),
#                                'html')

#             token_data.TokenStatus = "inactive"
#             token_data.FormStatus = "submitted"

#             enrollform = Enrollmentform.query.get(token_data["FormID"])
#             enrollform.PendingFrom = "employer"
#             db.session.commit()

#             new_token = Token(FormID=token_data["FormID"],
#                             FormCreatedDate=token_data["FormCreatedDate"],
#                             FormStatus="pending",
#                             FormType=token_data["FormType"],
#                             InitiatedBy=token_data["InitiatedBy"],
#                             # InitiatedDate=
#                             PendingFrom="employer",
#                             TokenStatus="active",
#                             EmployerID=token_data["EmployerID"],
#                             OlderTokenID=tokenID,
#                         )

#             db.session.add(new_token)
#             db.session.commit()
#             print(new_token.TokenID)

#             try:
#                 msg.attach(msgtext)
#                 smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
#                 smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
#                 return jsonify({"result": "success"}), 200
#             except Exception as e:
#                 print(str(e))
#                 file = open("log.txt", "a+")
#                 file.writelines(str(datetime.utcnow()) + "/n" + str(e) + "/n")
#                 file.close()
#                 return jsonify({"error": "Something wrong happened while sending the mail"}), 500
#         elif request_type == "save_formData":
#             print("savingformdata")
#             print(request.form["enrollmentFormData"])
#             enroll_form_data = json.loads(request.form.get("enrollmentFormData"))
#             if 'file' in request.files:
#                 print("hello")
#                 file = request.files["file"]
#                 filename = secure_filename(file.filename)
#                 print(filename)
#                 path = os.path.join(path, 'Employers')
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 path = os.path.join(path, employer_id)
#                 print(employer_id)
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 path = os.path.join(path, "enrollment")
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 path = os.path.join(path, request.form["tokenID"])
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 file.save(os.path.join(path, filename))
#                 enroll_form_data["filename"] = filename

#             # getting id from tokens
#             print(tokenID)
#             print(token_data)
#             print(request.form["enrollmentFormData"])
#             print(token_data["id"])
#             dob = enroll_form_data["dob"]
#             formcreateddate = enroll_form_data["formCreatedDate"]
#             if not dob == "":
#                 enroll_form_data["dob"] = datetime.strptime(str(dob).split("T")[0], "%Y-%m-%d")
#             # print(enroll_form_data["memberLastName"])
#             if not formcreateddate == "":
#                 str(formcreateddate).split(" ")

#             enrollform = Enrollmentform.query.get(token_data["FormID"])
#             enroll_form_data.DOB = enroll_form_data["dob"]

#             return jsonify({"result": "success"}), 200
#         elif request_type == "employer_submission":
#             enroll_form_data = json.loads(request.form.get("enrollmentFormData"))
#             print(enroll_form_data)
#             if 'file' in request.files:
#                 print("hello")
#                 file = request.files["file"]
#                 filename = secure_filename(file.filename)
#                 print(filename)
#                 path = os.path.join(path, "Employers/")
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 path = os.path.join(path, employer_id)
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 path = os.path.join(path, "enrollment")
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 path = os.path.join(path, request.form["tokenID"])
#                 if not os.path.exists(path):
#                     os.mkdir(path)
#                 file.save(os.path.join(path, filename))
#                 enroll_form_data["filename"] = filename
#             enroll_form_data["PendingFrom"] = "reviewermanager"
#             token_data.PendingFrom = "reviewermanager"
#             enrollform = Enrollmentform.query.filter_by(tokenID=token_data["TokenID"]).first()
#             for column_name in [column.key for column in Enrollmentform.__table__.columns]:
#                 if column_name in enroll_form_data:
#                     enrollform[column_name] = enroll_form_data[column_name]
#             db.session.commit()
#             return jsonify({"result": "success"}), 200


# @enrollment_blueprint.route("/enrollment", methods=['GET', 'POST', 'OPTIONS'])
# @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
# def send_enrollment():
#     token_id = request.args["TokenID"]

#     if request.method == "GET":
#         tokendata = Token.query.get(token_id)
#         print(tokendata)
#         if tokendata is not None:
#             formdata = Enrollmentform.query.filter_by(tokenID=tokendata["TokenID"]).first()
#             print(formdata)
#             return jsonify({"result": formdata}), 200
#         else:
#             return jsonify({"error": "Bad Request"}), 400
#     if request.method == "POST":
#         print(request.get_data())
#         data = json.loads(str(request.get_data(), encoding='utf-8'))
#         print(data)
#         member_name = data["membername"]
#         member_email = data["email"]
#         request_type = data["request_type"]
#         msgtext = ""
#         msg = MIMEMultipart()
#         msg['from'] = "venkatesh"
#         msg['to'] = member_name
#         smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
#         if request_type == "remainder":
#             notify = data["notify"]
#             try:
#                 token_data = Token.query.get(token_id)
#                 form_data = Enrollmentform.query.filter_by(tokenID=token_data["TokenID"]).first()
#                 if "formCreatedDate" in form_data.keys():
#                     # init_time = datetime.strptime(form_data["formCreatedDate"], "%d%m%Y %H:%M:%S.%f")
#                     # time = (datetime.utcnow() - form_data["formCreatedDate"]).days
#                     msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
#                     msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
#                                        ' Please do not reply to this message. **</p>'
#                                        '<p>Dear %s</p>'
#                                        '<p>Please click here. Otherwise, '
#                                        'cut and paste the link below into a browser, fill in the '
#                                        'required information, and when you are done'
#                                        ' hit the submit button to start your enrollment '
#                                        'into the plan.</p>'
#                                        '<p>-----------------------------------------</p>'
#                                        '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
#                                        '<p>To learn more about the Silver Thatch Pension Plan,'
#                                        ' click here to review our members handbook. </p>' % (member_name, token),
#                                        'html')
#                     # if time == 3:
#                     #     notify = True
#                     # elif time > 3:
#                     #     if "notifytime" in form_data:
#                     #         # notify_time = datetime.strptime(form_data["notifytime"], "%d%m%Y %H:%M:%S.%f")
#                     #         time_days = (datetime.utcnow() - form_data["notifytime"]).days
#                     #         if time_days == 3:
#                     #             notify = True
#                     if notify:
#                         msg.attach(msgtext)
#                         smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
#                         smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
#                         return jsonify({"result": "success"}), 200

#             except KeyError as e:
#                 print(str(e))
#                 file = open("log.txt", "a+")
#                 file.writelines(str(datetime.utcnow()) + str(e))
#                 file.close()
#                 return jsonify({"error": "Something wrong happened"}), 500
#             except Exception as e:
#                 print(str(e))
#                 file = open("log.txt", "a+")
#                 file.writelines(str(datetime.utcnow()) + str(e))
#                 file.close()
#                 return jsonify({"error": "Something wrong happened"}), 500

#         elif request_type == "approval_confirmation":
#             msg['subject'] = "Your Enrollment has been submitted"
#             msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
#                                ' Please do not reply to this message. **</p>'
#                                '<p>Dear %s</p>'
#                                '<p>Your Enrollment has been processed </p>' % (
#                                    member_name),
#                                'html')

#             tkn = Token.query.get(token_id)
#             tkn.status = "approved"
#             db.session.commit()

#             try:
#                 msg.attach(msgtext)
#                 smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
#                 smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
#                 return jsonify({"result": "success"}), 200
#             except Exception as e:
#                 print(str(e))
#                 file = open("log.txt", "a+")
#                 file.writelines(str(datetime.utcnow()) + str(e))
#                 file.close()
#                 return jsonify({"error": "Something wrong happened while sending the mail"}), 500

#         elif request_type == "rejected":
#             msg['subject'] = "Your Enrollment has been rejected"
#             msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
#                                ' Please do not reply to this message. **</p>'
#                                '<p>Dear %s</p>'
#                                '<p>Your Enrollment has been rejected </p>'
#                                '<p>Please click here. Otherwise, cut and paste the link below into a browser, '
#                                'fill in the required information, and when you are done hit the submit button to '
#                                'start your enrollment into the plan.</p>'
#                                '<p>%s</p>'
#                                '<p>-----------------------------------</p>'
#                                '<p>http://183.82.0.186:812/enrollment-form/%s</p>'
#                                '<p>To learn more about the Silver Thatch Pension '
#                                'Plan, click here to review our members handbook. </p>' % (
#                                    member_name, data["comments"], token),
#                                'html')
#             try:
#                 msg.attach(msgtext)
#                 smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
#                 smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
#                 return jsonify({"result": "success"}), 200
#             except Exception as e:
#                 print(str(e))
#                 file = open("log.txt", "a+")
#                 file.writelines(str(datetime.utcnow()) + str(e))
#                 file.close()
#                 return jsonify({"error": "Something wrong happened while sending the mail"}), 500
