from flask_restplus import Api


def init_app(app):
    from . import aux, index, user, enrollment, file
    from .auth import token_check, login
