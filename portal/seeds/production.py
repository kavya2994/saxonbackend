from portal.models.security_question import SecurityQuestion


class ProductionSeeder(object):
    def __init__(self, db):
        self.db = db

    def run(self):
        self._add_sec_questions()
        self.db.session.commit()

    def _add_sec_questions(self):
        q1 = SecurityQuestion(SecurityQuestionID=1)
        q1.Question = "What is your first school's name?"
        self.db.session.merge(q1)

        q2 = SecurityQuestion(SecurityQuestionID=2)
        q2.Question = "What is your first phone number?"
        self.db.session.merge(q2)

        q3 = SecurityQuestion(SecurityQuestionID=3)
        q3.Question = "What is your first pet's name?"
        self.db.session.merge(q3)
