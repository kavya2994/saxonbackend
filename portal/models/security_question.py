from . import db


class SecurityQuestion(db.Model):
    __bind_key__ = 'writeonly'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    question = db.Column(db.String(255))


# {'id': '2', 'question': 'What is your first phone number?'},
#  {'id': '3', 'question': "What is your first pet's name?"},
#  {'id': '1', 'question': "What is your first school's name?"}
