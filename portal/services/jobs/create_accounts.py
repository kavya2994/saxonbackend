from datetime import datetime

from ... import APP, LOG
from ...models import db
from ...models.users import Users
from ...models.member_view import MemberView
from ...models.employer_view import EmployerView
from ...models.roles import *
from ...models.status import *

def send_temporary_passwords():
    users = Users.query.filter(Users.Password.is_(None)).all()

def create_accounts(app):
    with app.app_context():
        employers = EmployerView.query.all()
        for employer in employers:
            user = Users(UserID=employer.ERKEY,
                         Username=employer.ERNO,
                         Email=employer.EMAIL,
                         Role=ROLES_EMPLOYER,
                         Status=STATUS_ACTIVE,
                         UserCreatedTime=datetime.utcnow())
            db.session.merge(user)
            db.session.commit()