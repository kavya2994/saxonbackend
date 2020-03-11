from flask_restx import Api


def init_app(app):
    # from . import aux, index
    from . import index
    from .auth import token_check, login, security_questions, get_securityquestion_user
    from .auth.password import reset, change
    from .file import download, explorer
    from .file.explorer import open, explorer, operation, operations, zip_download
    from .user import new, user, security_question, update_profile_details, get_profile_details
    from .enrollment import controller, simple_controller, initiate_controller
    from .termination import initiate_controller, controller, get_termination
    from .beneficiary import controller
    from .admin import new, update, delete, add_employer_to_member, get_internal_users, get_settings, new_settings, get_employer_to_member, get_user_data, delete_employer_to_member
    from .Subsidiaries import add_subsidiaries, delete_subsidiaries, get_subsidiary
    from .member import get_member_details, member_termination_details
    from .accounts import get_employers, get_members, search, get_members_for_employer, get_member_count, export_accounts
    from .messages import get_messages, create_message, delete_message
    from .health import status
    from .forms import forms_with_employees, forms_queue, myforms, controller, search
    from .Contributions import get_contributions, initiate_controller, download_excel, controller

    app.logger.info('Initialized routes')
