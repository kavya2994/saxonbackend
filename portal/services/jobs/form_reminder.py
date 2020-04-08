import smtplib
import time
from datetime import datetime

from ... import LOG
from ...models import db
from ...models.enrollmentform import Enrollmentform
from ...models.terminationform import Terminationform
from ...models.token import Token
from ...models.status import *
from ...models.roles import *
from ... import APP
from ...models.users import Users
from ...services.mail import send_email


def send_form_reminder(app):
    with app.app_context():
        LOG.info("Running the form reminder scheduled job")
        enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
            Token.FormID == Enrollmentform.FormID,
            Token.FormStatus == STATUS_PENDING,
            Token.PendingFrom == ROLES_MEMBER,
            Token.TokenStatus == STATUS_ACTIVE,
            Token.FormType == "Enrollment").all()

        for tokens, enrollments in enrollment_form_data:
            if enrollments.LastNotifiedDate is None:

                if tokens.InitiatedDate is not None and (datetime.utcnow() - tokens.InitiatedDate).days == 3:
                    subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg_text = f'<p>**This is an auto-generated e-mail message.' \
                               f' Please do not reply to this message. **</p>' \
                               f'<p>Dear {enrollments.FirstName + " " + enrollments.LastName}</p>' \
                               f'<p>Please click <a href="{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}">' \
                               f'here</a>. Otherwise, ' + \
                               f'cut and paste the link below into a browser, fill in the ' \
                               f'required information, and when you are done' \
                               f' hit the submit button to start your enrollment ' \
                               f'into the plan.</p>' \
                               f'<p>-----------------------------------------</p>' \
                               f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}</p>' \
                               f'<p>To learn more about the Silver Thatch Pension Plan,' \
                               f' click <a href="{APP.config["MAIL_ENROLLMENT_URL"]}">here</a>' \
                               f' to review our members handbook. </p>'
                    try:
                        send_email(to_address=enrollments.EmailAddress, subject=subject, body=msg_text)
                        enrollments.LastNotifiedDate = datetime.utcnow()
                        db.session.commit()
                    except Exception as e:
                        LOG.error(e)
            else:
                if (datetime.utcnow() - enrollments.LastNotifiedDate).days == 3:
                    subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg_text = f'<p>**This is an auto-generated e-mail message.' \
                               f' Please do not reply to this message. **</p>' \
                               f'<p>Dear {enrollments.FirstName + " " + enrollments.LastName}</p>' \
                               f'<p>Please click <a href="{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}">' \
                               f'here</a>. Otherwise, ' \
                               f'cut and paste the link below into a browser, fill in the ' \
                               f'required information, and when you are done' \
                               f' hit the submit button to start your enrollment ' \
                               f'into the plan.</p>' \
                               f'<p>-----------------------------------------</p>' \
                               f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}</p>' \
                               f'<p>To learn more about the Silver Thatch Pension Plan,' \
                               f' click <a href="{APP.config["MAIL_ENROLLMENT_URL"]}">here</a> ' \
                               f'to review our members handbook. </p>'
                    try:
                        send_email(to_address=enrollments.EmailAddress, subject=subject, body=msg_text)
                        enrollments.LastNotifiedDate = datetime.utcnow()
                        db.session.commit()
                    except Exception as e:
                        LOG.error(e)
        termination_form_data = db.session.query(Token, Terminationform).filter(
            Token.FormID == Terminationform.FormID,
            Token.FormStatus == STATUS_PENDING,
            Token.PendingFrom == ROLES_MEMBER,
            Token.TokenStatus == STATUS_ACTIVE,
            Token.FormType == "Termination").all()
        for tokens, termination in termination_form_data:
            if termination.LastNotifiedDate is None:
                if tokens.InitiatedDate is not None and (datetime.utcnow() - tokens.InitiatedDate).days == 3:
                    subject = "Please complete your Silver Thatch Pensions Employment Termination Form"
                    msg_text = f'<p>**This is an auto-generated e-mail message.' \
                               f' Please do not reply to this message. **</p>' \
                               f'<p>Dear {termination.MemberName}</p>' \
                               f'<p>In an effort to keep you connected with your Silver Thatch Pension ' \
                               f'after you leave your current position, please click here or copy the link ' \
                               f'below into a browser to complete the termination of employment form. This ' \
                               f'form notifies us that you are no longer employed with your current ' \
                               f'employer and allows Silver Thatch Pensions to stay in touch with you in ' \
                               f'regards to your pension. </p> ' \
                               f'<p>-----------------------------------------</p>' \
                               f'<p>{APP.config["FRONTEND_URL"]}/terminationform/{tokens.TokenID}</p>'
                    try:
                        send_email(to_address=termination.EmailAddress, subject=subject, body=msg_text)
                        enrollments.LastNotifiedDate = datetime.utcnow()
                        db.session.commit()
                    except smtplib.SMTPException as e:
                        LOG.error(e)
                        continue
                    except Exception as e:
                        LOG.error(e)
                        continue

            else:
                if (datetime.utcnow() - enrollments.LastNotifiedDate).days == 3:
                    subject = "Please complete your Silver Thatch Pensions Employment Termination Form"
                    msg_text = f'<p>**This is an auto-generated e-mail message.' \
                               f' Please do not reply to this message. **</p>' \
                               f'<p>Dear {termination.MemberName}</p>' \
                               f'<p>In an effort to keep you connected with your Silver Thatch Pension ' \
                               f'after you leave your current position, please click here or copy the link ' \
                               f'below into a browser to complete the termination of employment form. This ' \
                               f'form notifies us that you are no longer employed with your current ' \
                               f'employer and allows Silver Thatch Pensions to stay in touch with you in ' \
                               f'regards to your pension. </p> ' \
                               f'<p>-----------------------------------------</p>' \
                               f'<p>{APP.config["FRONTEND_URL"]}/terminationform/{tokens.TokenID}</p>'
                    try:
                        send_email(to_address=termination.EmailAddress, subject=subject, body=msg_text)
                        enrollments.LastNotifiedDate = datetime.utcnow()
                        db.session.commit()
                    except smtplib.SMTPException as e:
                        LOG.error(e)
                        continue
                    except Exception as e:
                        LOG.error(e)
                        continue
        #     For Reminding the employer
        enrollment_form_data_employer = db.session.query(Token, Enrollmentform).filter(
            Token.FormID == Enrollmentform.FormID,
            Token.FormStatus == STATUS_PENDING,
            Token.PendingFrom == ROLES_EMPLOYER,
            Token.TokenStatus == STATUS_ACTIVE,
            Token.FormType == "Enrollment").all()

        for tokens, enrollments in enrollment_form_data_employer:
            if enrollments.LastNotifiedDate is not None:
                employer = Users.query.filter(Users.Username == enrollments.EmployerID,
                                              Users.Role == ROLES_EMPLOYER,
                                              Users.Email.isnot(None)).first()
                if (datetime.utcnow() - enrollments.LastNotifiedDate).days == 3:
                    subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                    msg_text = f'<p>**This is an auto-generated e-mail message.' \
                               f' Please do not reply to this message. **</p>' \
                               f'<p>Dear {enrollments.EmployerName}</p>' \
                               f'<p>Please click <a href="{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}">' \
                               f'here</a>. Otherwise, ' + \
                               f'cut and paste the link below into a browser, fill in the ' \
                               f'required information, and when you are done' \
                               f' hit the submit button to start your enrollment ' \
                               f'into the plan.</p>' \
                               f'<p>-----------------------------------------</p>' \
                               f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}</p>' \
                               f'<p>To learn more about the Silver Thatch Pension Plan,' \
                               f' click <a href="{APP.config["MAIL_ENROLLMENT_URL"]}">here</a>' \
                               f' to review our members handbook. </p>'
                    try:
                        if employer.Email == "":
                            continue
                        send_email(to_address=employer.Email, subject=subject, body=msg_text)
                        enrollments.LastNotifiedDate = datetime.utcnow()
                        db.session.commit()
                    except smtplib.SMTPException as e:
                        LOG.error(e)
                        continue
                    except Exception as e:
                        LOG.error(e)
                        continue

        termination_form_data_employer = db.session.query(Token, Terminationform).filter(
            Token.FormID == Terminationform.FormID,
            Token.FormStatus == STATUS_PENDING,
            Token.PendingFrom == ROLES_MEMBER,
            Token.TokenStatus == STATUS_ACTIVE,
            Token.FormType == "Termination").all()
        for tokens, termination in termination_form_data_employer:
            employer = Users.query.filter(Users.Username == termination.EmployerID,
                                          Users.Role == ROLES_EMPLOYER,
                                          Users.Email.isnot(None)).first()
            if termination.LastNotifiedDate is not None:
                if (datetime.utcnow() - termination.LastNotifiedDate).days == 3:
                    subject = "Please complete your Silver Thatch Pensions Employment Termination Form"
                    msg_text = f'<p>**This is an auto-generated e-mail message.' \
                               f' Please do not reply to this message. **</p>' \
                               f'<p>Dear {termination.EmployerName}</p>' \
                               f'<p>please click here or copy the link below into a browser to complete' \
                               f' the termination of one of your employee. </p> ' \
                               f'<p>-----------------------------------------</p>' \
                               f'<p>{APP.config["FRONTEND_URL"]}/terminationform/{tokens.TokenID}</p>'
                    try:
                        if employer.Email == "":
                            continue
                        send_email(to_address=employer.Email, subject=subject, body=msg_text)
                        enrollments.LastNotifiedDate = datetime.utcnow()
                        db.session.commit()
                    except smtplib.SMTPException as e:
                        LOG.error(e)
                        continue
                    except Exception as e:
                        LOG.error(e)
                        continue

        LOG.info("Scheduler Job done for today")
