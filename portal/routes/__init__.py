from flask_restplus import Api


def init_app(app):
    from . import aux, index
    from .auth import token_check, login, security_questions
    from .auth.password import reset, change
    from .file import download, explorer
    from .file.explorer import open, explorer, operation, operations
    from .user import new, user, security_question
    from .enrollment import get, initiate, file, send
    from .termination import initiate, send
