from portal.models.users import Users


class DemoSeeder(object):
    def __init__(self, db):
        self.db = db

    def run(self):
        user = Users(Username="saxon", Password="test")
        print("Adding user: %s" % user)
        self.db.session.add(user)
        self.db.session.commit()
