from portal.models.security_question import SecurityQuestion


class ProductionSeeder(object):
    def __init__(self, db):
        self.db = db

    def run(self):
        self._add_sec_questions()
        self.db.session.commit()

    def _add_sec_questions(self):
        q1 = SecurityQuestion(SecurityQuestionID=1)
        q1.Question = "What is your favourite sports team?"
        self.db.session.merge(q1)

        q2 = SecurityQuestion(SecurityQuestionID=2)
        q2.Question = "What is the name of your first pet?"
        self.db.session.merge(q2)

        q3 = SecurityQuestion(SecurityQuestionID=3)
        q3.Question = "What is your high school mascot?"
        self.db.session.merge(q3)

        q4 = SecurityQuestion(SecurityQuestionID=4)
        q4.Question = "What city were you born in?"
        self.db.session.merge(q4)

        q5 = SecurityQuestion(SecurityQuestionID=5)
        q5.Question = "What is your mother's maiden name?"
        self.db.session.merge(q5)

        q6 = SecurityQuestion(SecurityQuestionID=6)
        q6.Question = "Where did your parents meet?"
        self.db.session.merge(q6)

        q7 = SecurityQuestion(SecurityQuestionID=7)
        q7.Question = "What was your childhood phone number?"
        self.db.session.merge(q7)

        q8 = SecurityQuestion(SecurityQuestionID=8)
        q8.Question = "Where were you New Years 2000?"
        self.db.session.merge(q8)

        q9 = SecurityQuestion(SecurityQuestionID=9)
        q9.Question = "Where were you New Years 2000?"
        self.db.session.merge(q9)

        q10 = SecurityQuestion(SecurityQuestionID=10)
        q10.Question = "What is the name of the place your wedding reception was held?"
        self.db.session.merge(q10)

        q11 = SecurityQuestion(SecurityQuestionID=11)
        q11.Question = "What was the make and model of your first car?"
        self.db.session.merge(q11)

        q12 = SecurityQuestion(SecurityQuestionID=12)
        q12.Question = "What was your maternal grandfather's first name?"
        self.db.session.merge(q12)

        q13 = SecurityQuestion(SecurityQuestionID=13)
        q13.Question = "what is the first musical instrument you learned to play?"
        self.db.session.merge(q13)

        q14 = SecurityQuestion(SecurityQuestionID=14)
        q14.Question = "If you could witness any event(past,present or future), what would it be?"
        self.db.session.merge(q14)



