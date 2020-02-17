from flask_restplus import Api


def init_app(app):
    # from . import aux, index
    from . import index
    from .auth import token_check, login, security_questions
    from .auth.password import reset, change
    from .file import download, explorer
    from .file.explorer import open, explorer, operation, operations
    from .user import new, user, security_question, update_profile_details, get_profile_details
    from .enrollment import controller, simple_controller, initiate_controller, file, send
    from .termination import initiate, send
    from .beneficiary import controller
    from .admin import new, update, delete, get_employers, get_members, add_employer_to_member
    from .Subsidiaries import add_subsidiaries, delete_subsidiaries, get_subsidiary
    from .member import get_member_details, member_termination_details
