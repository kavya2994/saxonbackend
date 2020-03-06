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
from ...services.mail import send_email


def send_form_reminder():
    LOG.info("Running the form reminder scheduled job")
    enrollment_form_data = db.session.query(Token, Enrollmentform).filter(
        Token.FormID == Enrollmentform.FormID,
        Token.FormStatus == STATUS_PENDING,
        Token.PendingFrom == ROLES_MEMBER,
        Token.TokenStatus == STATUS_ACTIVE).all()

    for tokens, enrollments in enrollment_form_data:
        if enrollments.LastNotifiedDate is not None:
            continue

        if tokens.InitiatedDate is not None and datetime.utcnow() - tokens.InitiatedDate == 1:
            subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
            msg_text = f'<p>**This is an auto-generated e-mail message.' + \
                       f' Please do not reply to this message. **</p>' + \
                       f'<p>Dear %s</p>' + \
                       f'<p>Please click here. Otherwise, ' + \
                       f'cut and paste the link below into a browser, fill in the ' + \
                       f'required information, and when you are done' + \
                       f' hit the submit button to start your enrollment ' + \
                       f'into the plan.</p>' + \
                       f'<p>-----------------------------------------</p>' + \
                       f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}</p>' + \
                       f'<p>To learn more about the Silver Thatch Pension Plan,' + \
                       f' click here to review our members handbook. </p>'
            send_email(to_address=enrollments.EmailAddress, subject=subject, body=msg_text)
            enrollments.LastNotifiedDate = datetime.utcnow()
        else:
            if datetime.utcnow() - tokens.LastNotifiedDate == 1:
                subject = "Your Silver Thatch Pensions Enrollment Form needs to be completed"
                msg_text = f'<p>**This is an auto-generated e-mail message.' + \
                           f' Please do not reply to this message. **</p>' + \
                           f'<p>Dear %s</p>' + \
                           f'<p>Please click here. Otherwise, ' + \
                           f'cut and paste the link below into a browser, fill in the ' + \
                           f'required information, and when you are done' + \
                           f' hit the submit button to start your enrollment ' + \
                           f'into the plan.</p>' + \
                           f'<p>-----------------------------------------</p>' + \
                           f'<p>{APP.config["FRONTEND_URL"]}/enrollment-form/{tokens.TokenID}</p>' + \
                           f'<p>To learn more about the Silver Thatch Pension Plan,' + \
                           f' click here to review our members handbook. </p>'
                send_email(to_address=enrollments.EmailAddress, subject=subject, body=msg_text)
                enrollments.LastNotifiedDate = datetime.utcnow()
    termination_form_data = db.session.query(Token, Terminationform).filter(
        Token.FormID == Terminationform.FormID,
        Token.FormStatus == STATUS_PENDING,
        Token.PendingFrom == ROLES_MEMBER,
        Token.TokenStatus == STATUS_ACTIVE).all()
    LOG.info("Scheduler Job done for today")
