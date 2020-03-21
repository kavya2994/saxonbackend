from datetime import datetime
from threading import Thread

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


def send_temporary_passwords(app):
    with app.app_context():
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
                continue
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
    LOG.info("Started creating accounts background job")
    with app.app_context():
        # users = Users.query.filter(Users.Password.is_(None)).all()
        # print(users)
        # send_temporary_passwords()
        LOG.debug("Starting creating employers accounts")
        employers = EmployerView.query.all()
        LOG.debug("Employers fetched: %s", len(employers))
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

        Thread(target=send_temporary_passwords, args=(app,)).start()
        LOG.debug("Starting creating member accounts")
        offset_ = 0
        count = MemberView.query.count()
        count = int(count / 100) + 1
        for i in range(count):
            try:
                LOG.debug("Going to fetch %s members from offset %s", count, offset_)
                members = MemberView.query.offset(offset_).limit(100).all()
                LOG.debug("%s members fetched successfully from offset %s", len(members), offset_)
                for member in members:
                    try:
                        user = Users(UserID=member.MKEY,
                                     Username=member.MEMNO,
                                     Email=member.EMAIL,
                                     DisplayName=member.FNAME if member.FNAME is not None else "" + " " + member.LNAME if member.LNAME is not None else "",
                                     Role=ROLES_MEMBER,
                                     Status=STATUS_ACTIVE)
                        db.session.merge(user)
                        db.session.commit()
                    except Exception as e:
                        LOG.error("There was an unexpected error while creating new user from MembersView. %s", e)
                        continue
                Thread(target=send_temporary_passwords, args=(app,)).start()
            except Exception as e:
                LOG.error("There was an unexpected error while processing MembersView items. %s",e)

            offset_ += 99
