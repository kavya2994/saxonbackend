from datetime import datetime

from ..mail import send_email
from ... import APP, LOG
from ...encryption import Encryption
from ...models import db
from ...models.users import Users
from ...models.member_view import MemberView
from ...models.employer_view import EmployerView
from ...models.roles import *
from ...models.status import *
from ...helpers import randomStringwithDigitsAndSymbols


def send_temporary_passwords():
    users = Users.query.filter(Users.Password.is_(None)).all()
    for user in users:
        try:
            random_password = randomStringwithDigitsAndSymbols()
            enc_random_pass = Encryption().encrypt("test")
            user.Password = enc_random_pass
            user.TemporaryPassword = True
            user.UserCreatedTime = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            LOG.error(e)
        # msg_text = f'<p>Dear {user.DisplayName}</p>' + \
        #            f'<p>Your account has been created</p>' + \
        #            f'<p>Username is {user.Username}</p>' + \
        #            f'<p> please use this password {"test"} to log in</p>' + \
        #            f'<p> Please ensure that you are not copying any extra spaces</p>' \
        #            f'<p>Please use below link to login</p>' \
        #            f'<p>{APP.config["FRONTEND_URL"]}/login</p>'
        # if user.Email is not None:
        #     send_email(user.Email, "Welcome to Pension Management portal", body=msg_text)


def create_accounts(app):
    with app.app_context():
        # users = Users.query.filter(Users.Password.is_(None)).all()
        # print(users)
        send_temporary_passwords()
        employers = EmployerView.query.all()

        for employer in employers:
            try:
                user = Users(UserID=employer.ERKEY,
                             Username=employer.ERNO,
                             Email=employer.EMAIL,
                             DisplayName=employer.ENAME,
                             Role=ROLES_EMPLOYER,
                             Status=STATUS_INACTIVE if employer.TERMDATE is not None and employer.TERMDATE < datetime.utcnow() else STATUS_ACTIVE)
                db.session.merge(user)
                db.session.commit()
            except Exception as e:
                LOG.error(e)
                continue

        members = MemberView.query.all()

        for member in members:
            try:
                user = Users(UserID=member.ERKEY,
                             Username=member.ERNO,
                             Email=member.EMAIL,
                             DisplayName=member.FNAME if member.FNAME is not None else "" + " " + member.LNAME if member.LNAME is not None else "",
                             Role=ROLES_MEMBER,
                             Status=STATUS_ACTIVE)
                db.session.merge(user)
                db.session.commit()
            except Exception as e:
                LOG.error(e)
                continue
        send_temporary_passwords()
