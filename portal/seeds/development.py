from portal.models.users import Users
from portal.models.roles import *

class DevelopmentSeeder(object):
    def __init__(self, db):
        self.db = db

    def run(self):
        self._add_users()
        self.db.session.commit()

    def _add_users(self):
        admin_user = Users(Username="saxon",
            Password="6Q9usKHCRmlaNgufji0mJg==",
            Status="active",
            TemporaryPassword=False,
            Role=ROLES_ADMIN,
            SecurityQuestionID=1)

        employer_user = Users(Username="saxonemployer",
            Password="6Q9usKHCRmlaNgufji0mJg==",
            Status="active",
            TemporaryPassword=True,
            Role=ROLES_EMPLOYER,
            SecurityQuestionID=1)

        self.db.session.merge(admin_user)
        self.db.session.merge(employer_user)
