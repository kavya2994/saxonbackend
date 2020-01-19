import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from ..helpers import token_verify


enrollment_blueprint = Blueprint('enrollment_blueprint', __name__, template_folder='templates')

@enrollment_blueprint.route("/initiate_enrollment", methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def send_enrollment_form():
    if request.method == "POST":
        print(request.headers)
        if "Authorization" in request.headers.keys() and token_verify(token=request.headers["Authorization"],
                                                                      ip=request.headers["Ipaddress"],
                                                                      user=request.headers["User"]):
            try:
                auth = request.headers["Authorization"]
                auth = jwt.decode(auth, key='secret')
                if auth["role"] == "employer":
                    data = json.loads(str(request.get_data(), encoding='utf-8'))
                    member_email = data["email"]
                    employer_id = data["employernumber"]
                    # employer_name = data["employername"]
                    member_name = data["memberfirstName"]
                    # form_type = data["formType"]
                    employer_comments = data["comments"]
                    print(data)

                    smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
                    msg = MIMEMultipart()
                    msg['subject'] = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg['from'] = "venkatesh"
                    msg['to'] = member_name
                    employernumber = employer_id

                    try:
                        data["formCreatedDate"] = datetime.utcnow()
                        if str(employer_id)[-2:].__contains__("HR"):
                            employernumber = str(employer_id)[:-2]
                        print(employernumber)
                        myform_enroll = db1.collection("myforms").add(data)
                        token_data = db1.collection("Tokens").add(
                            {"id": myform_enroll[1].id, "initiatedBy": employer_id, "tokenStatus": "active",
                             # "tokenType": "enrollment",
                             "formCreatedDate": datetime.utcnow(),
                             "pendingFrom": "member",
                             "formType": "Enrollment",
                             "status": "pending",
                             "employernumber": employernumber,
                             "memberfirstName": member_name})
                        token = token_data[1].id
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
                        return jsonify({"result": "Success"}), 200
                    except Exception as e:
                        return jsonify({"error": "Something wrong happened"}), 500
                else:
                    print("role is not employer")
                    return jsonify({"error": "UnAuthorised"}), 401

            except Exception as e:
                print(str(e))
                return jsonify({"error": "UnAuthorised"}), 401
        else:
            print("role is not employer")
            return jsonify({"error": "UnAuthorised"}), 401


@enrollment_blueprint.route("/delete_enrollment_file", methods=['POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def deleteenrollmentfile():
    if request.method == "POST":
        base_path = os.path.join(DATA_DIR, 'Employers')
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        employer = data["employerid"]
        path = data["path"]
        base_path = os.path.join(base_path, employer, path)
        if os.path.exists(base_path) and os.path.isfile(base_path):
            try:
                os.remove(base_path)
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                return jsonify({"error": "Can't delete the file"}), 500
        else:
            return jsonify({"error": "Bad request"}), 400


@enrollment_blueprint.route("/save_enrollment", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def save_enrollment():
    if request.method == "POST":
        member_name = request.form.get("membername")
        token = request.form.get("tokenID")
        member_email = request.form.get("email")
        type = request.form.get("request_type")
        employer_id = request.form.get("employerusername")
        path = DATA_DIR
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if type == "member_submission":
            msg['subject'] = "Your Enrollment has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment was submitted on %s. '
                               'You will receive notification once your form has been processed</p>' % (
                                   member_name, datetime.utcnow().strftime("%Y-%m-%d")),
                               'html')
            member_token_data = db1.collection("Tokens").document(token).get().to_dict()
            new_token_data = member_token_data
            new_token_data["pendingFrom"] = "employer"
            new_token_data["oldToken"] = token
            new_token_data["status"] = "pending"
            new_token_data["tokenStatus"] = "active"
            db1.collection("Tokens").document(token).update({"tokenStatus": "inactive", "status": "submitted"})
            db1.collection("myforms").document(member_token_data["id"]).update({"pendingFrom": "employer"})
            new_token = db1.collection("Tokens").add(new_token_data)
            print(new_token[1].id)
            try:
                msg.attach(msgtext)
                smtpObj.login('venkateshvyyerram@gmail.com', "mynameisvenkatesh")
                smtpObj.sendmail("venkateshvyyerram@gmail.com", member_email, msg.as_string())
                return jsonify({"result": "success"}), 200
            except Exception as e:
                print(str(e))
                file = open("log.txt", "a+")
                file.writelines(str(datetime.utcnow()) + "/n" + str(e) + "/n")
                file.close()
                return jsonify({"error": "Something wrong happened while sending the mail"}), 500
        elif type == "save_formData":
            print("savingformdata")
            print(request.form["enrollmentFormData"])
            enroll_form_data = json.loads(request.form.get("enrollmentFormData"))
            if 'file' in request.files:
                print("hello")
                file = request.files["file"]
                filename = secure_filename(file.filename)
                print(filename)
                path = os.path.join(path, 'Employers')
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, employer_id)
                print(employer_id)
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, "enrollment")
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, request.form["tokenID"])
                if not os.path.exists(path):
                    os.mkdir(path)
                file.save(os.path.join(path, filename))
                enroll_form_data["filename"] = filename

            # getting id from tokens
            print(token)
            token_data = db1.collection("Tokens").document(token).get().to_dict()
            print(token_data)
            print(request.form["enrollmentFormData"])
            print(token_data["id"])
            dob = enroll_form_data["dob"]
            formcreateddate = enroll_form_data["formCreatedDate"]
            if not dob == "":
                enroll_form_data["dob"] = datetime.strptime(str(dob).split("T")[0], "%Y-%m-%d")
            # print(enroll_form_data["memberLastName"])
            if not formcreateddate == "":
                str(formcreateddate).split(" ")
            db1.collection("myforms").document(token_data["id"]).update(enroll_form_data)
            return jsonify({"result": "success"}), 200
        elif type == "employer_submission":
            enroll_form_data = json.loads(request.form.get("enrollmentFormData"))
            print(enroll_form_data)
            if 'file' in request.files:
                print("hello")
                file = request.files["file"]
                filename = secure_filename(file.filename)
                print(filename)
                path = os.path.join(path, "Employers/")
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, employer_id)
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, "enrollment")
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(path, request.form["tokenID"])
                if not os.path.exists(path):
                    os.mkdir(path)
                file.save(os.path.join(path, filename))
                enroll_form_data["filename"] = filename
            enroll_form_data["pendingFrom"] = "reviewermanager"
            token_data = db1.collection("Tokens").document(token).get().to_dict()
            db1.collection("Tokens").document(token).update({"pendingFrom": "reviewermanager"})
            db1.collection("myforms").document(token_data["id"]).update(enroll_form_data)
            return jsonify({"result": "success"}), 200


@enrollment_blueprint.route("/enrollment", methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(
    origins=['https://angularproject-5c26e.firebaseapp.com', 'http://localhost:4200', 'http://183.82.0.186:812',
             'http://192.168.2.146:812'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
def send_enrollment():
    if request.method == "GET":
        token = request.args["token"]
        tokendata = db1.collection("Tokens").document(token).get().to_dict()
        print(tokendata)
        if tokendata is not None and "id" in tokendata.keys():
            formdata = db1.collection("myforms").document(tokendata["id"]).get().to_dict()
            print(formdata)
            return jsonify({"result": formdata}), 200
        else:
            return jsonify({"error": "Bad Request"}), 400
    if request.method == "POST":
        print(request.get_data())
        data = json.loads(str(request.get_data(), encoding='utf-8'))
        print(data)
        member_name = data["membername"]
        token = data["tokenID"]
        member_email = data["email"]
        type = data["request_type"]
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        if type == "remainder":
            notify = data["notify"]
            try:
                token_data = db1.collection("Tokens").document(token).get().to_dict()
                form_data = db1.collection("myforms").document(token_data["id"]).get().to_dict()
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
                        db1.collection("myforms").document(token_data["id"]).update({"notifytime": datetime.utcnow()})
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

        elif type == "approval_confirmation":
            msg['subject'] = "Your Enrollment has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment has been processed </p>' % (
                                   member_name),
                               'html')
            db1.collection("Tokens").document(token).update({"status": "approved"})
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
        elif type == "rejected":
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
