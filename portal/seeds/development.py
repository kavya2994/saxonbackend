from portal.models.users import Users
from portal.models.roles import *
from portal.models.employer import Employer
from portal.models.status import *
from portal.models.member import Member


class DevelopmentSeeder(object):
    def __init__(self, db):
        self.db = db

    def run(self):
        self._add_users()
        self._add_employers()
        self._add_members()
        self.db.session.commit()

    def _add_users(self):
        admin_user = Users(UserID=1,
                           Username="saxon",
                           Password="6Q9usKHCRmlaNgufji0mJg==",
                           Status=STATUS_ACTIVE,
                           TemporaryPassword=False,
                           Role=ROLES_ADMIN,
                           SecurityQuestionID=1)

        employer_user = Users(UserID=2,
                              Username="saxonemployer",
                              Password="6Q9usKHCRmlaNgufji0mJg==",
                              Status=STATUS_ACTIVE,
                              TemporaryPassword=False,
                              Role=ROLES_EMPLOYER,
                              SecurityQuestionID=1)

        reviewmanager_user = Users(UserID=3,
                                   Username="saxonreviewmanager",
                                   Password="6Q9usKHCRmlaNgufji0mJg==",
                                   Status=STATUS_ACTIVE,
                                   TemporaryPassword=False,
                                   Role=ROLES_REVIEW_MANAGER,
                                   SecurityQuestionID=1)

        self.db.session.merge(admin_user)
        self.db.session.merge(employer_user)
        self.db.session.merge(reviewmanager_user)

    def _add_employers(self):
        employer1 = Employer(
            EmployerID=1,
            Username='employer-test-1',
            Displayname='Employer Test 1',
            Email='emp1@test.dev',
            Status='Active'
        )
        member1 = Member(
            MemberID=1,
            Username='member-test-1',
            DisplayName='Member Test 1',
            Email='member1@test.dev',
            Status='Active'
        )
        member2 = Member(
            MemberID=2,
            Username='member-test-2',
            DisplayName='Member Test 2',
            Email='member2@test.dev',
            Status='Active'
        )
        employer1.Members.append(member1)
        employer1.Members.append(member2)
        self.db.session.merge(employer1)

    def _add_members(self):
        member3 = Member(
            MemberID=3,
            Username='member-test-3',
            DisplayName='Member Test 3',
            Email='member3@test.dev',
            Status='Inactive'
        )
        member4 = Member(
            MemberID=4,
            Username='member-test-4',
            DisplayName='Member Test 4',
            Email='member4@test.dev',
            Status='Active'
        )
        self.db.session.merge(member3)
        self.db.session.merge(member4)
