import os
import jwt
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, jsonify, request
from flask_restplus import Resource, reqparse, cors
from werkzeug.utils import secure_filename
from ...helpers import token_verify, crossdomain
from ...models.enrollmentform import Enrollmentform
from ...models.token import Token
from ...models import db
from ...api import api
from . import ns
from ... import APP


parser = reqparse.RequestParser()
parser.add_argument('Authorization', type=str, location='headers', required=True)
parser.add_argument('username', type=str, location='headers', required=True)
parser.add_argument('Ipaddress', type=str, location='headers', required=True)


@ns.route("/file")
class EnrollmentFile(Resource):
    @crossdomain(whitelist=APP.config['CORS_ORIGIN_WHITELIST'], headers=APP.config['CORS_HEADERS'])
    def options(self):
        pass

    @ns.doc(parser=parser,
        description='Delete Enrollment File',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})

    @ns.expect(parser, validate=True)
    def delete(self):
        base_path = os.path.join(app.config['DATA_DIR'], 'Employers')
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

    @ns.doc(parser=None,
        description='Save Enrollment File',
        responses={200: 'OK', 400: 'Bad Request', 401: 'Unauthorized', 500: 'Internal Server Error'})
    # @cross_origin(origins=['*'], allow_headers=['Content-Type', 'Authorization', 'User', 'Ipaddress'])
    # @enrollment_blueprint.route("/save_enrollment", methods=['GET', 'POST', 'OPTIONS'])
    def post(self):
        member_name = request.form.get("membername")
        tokenID = request.form.get("tokenID")
        member_email = request.form.get("email")
        request_type = request.form.get("request_type")
        employer_id = request.form.get("employerusername")
        path = app.config['DATA_DIR']
        msgtext = ""
        msg = MIMEMultipart()
        msg['from'] = "venkatesh"
        msg['to'] = member_name
        smtpObj = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
        token_data = Token.query.get(tokenID)

        if request_type == "member_submission":
            msg['subject'] = "Your Enrollment has been submitted"
            msgtext = MIMEText('<p>**This is an auto-generated e-mail message.'
                               ' Please do not reply to this message. **</p>'
                               '<p>Dear %s</p>'
                               '<p>Your Enrollment was submitted on %s. '
                               'You will receive notification once your form has been processed</p>' % (
                                   member_name, datetime.utcnow().strftime("%Y-%m-%d")),
                               'html')

            token_data.TokenStatus = "inactive"
            token_data.FormStatus = "submitted"

            enrollform = Enrollmentform.query.get(token_data["FormID"])
            enrollform.PendingFrom = "employer"
            db.session.commit()

            new_token = Token(FormID=token_data["FormID"],
                            FormCreatedDate=token_data["FormCreatedDate"],
                            FormStatus="pending",
                            FormType=token_data["FormType"],
                            InitiatedBy=token_data["InitiatedBy"],
                            # InitiatedDate=
                            PendingFrom="employer",
                            TokenStatus="active",
                            EmployerID=token_data["EmployerID"],
                            OlderTokenID=tokenID,
                        )

            db.session.add(new_token)
            db.session.commit()
            print(new_token.TokenID)

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
        elif request_type == "save_formData":
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
            print(tokenID)
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

            enrollform = Enrollmentform.query.get(token_data["FormID"])
            enroll_form_data.DOB = enroll_form_data["dob"]

            return jsonify({"result": "success"}), 200
        elif request_type == "employer_submission":
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
            enroll_form_data["PendingFrom"] = "reviewermanager"
            token_data.PendingFrom = "reviewermanager"
            enrollform = Enrollmentform.query.filter_by(tokenID=token_data["TokenID"]).first()
            for column_name in [column.key for column in Enrollmentform.__table__.columns]:
                if column_name in enroll_form_data:
                    enrollform[column_name] = enroll_form_data[column_name]
            db.session.commit()
            return jsonify({"result": "success"}), 200
