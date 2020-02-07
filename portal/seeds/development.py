from portal.models.users import Users


class DevelopmentSeeder(object):
    def __init__(self, db):
        self.db = db

    def run(self):
        self._add_users()
        self.db.session.commit()

    def _add_users(self):
        test_user = Users(Username="saxon",
            Password="6Q9usKHCRmlaNgufji0mJg==",
            Status="active",
            SecurityQuestionID=1)

        self.db.session.merge(test_user)
