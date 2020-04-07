import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    readonly_db_connection_string = app.config['DBAAS_READONLY_CONNECTION_STRING'] \
        if 'DBAAS_READONLY_CONNECTION_STRING' in app.config else "sqlite:///../data/readonly.sqlite"

    writeonly_db_connection_string = app.config['DBAAS_WRITEONLY_CONNECTION_STRING'] \
        if 'DBAAS_WRITEONLY_CONNECTION_STRING' in app.config else "sqlite:///../data/writeonly.sqlite"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'readonly': readonly_db_connection_string,
        'writeonly': writeonly_db_connection_string,
    }

    db.init_app(app)
    app.logger.info('Initialized models')

    with app.app_context():
        from .comments import Comments
        from .contributionform import Contributionform
        from .employer import Employer
        from .member import Member
        from .employer_member_relation import EmpMemRel
        from .emp_mem_relation import EmpMemRelation
        from .enrollmentform import Enrollmentform
        from .jwttokenblacklist import JWTTokenBlacklist
        from .beneficiary import Beneficiary
        from .token import Token
        from .terminationform import Terminationform
        from .security_question import SecurityQuestion
        from .users import Users
        from .subsidiaries import Subsidiaries
        from .employer_view import EmployerView
        from .member_view import MemberView
        from .settings import Settings
        from .messages import Messages
        from .beneficiary_read import BeneficiaryFromRead
        from .annual_statement import AnnualStatements
        from .monthly_statements import MonthlyStatements
        from .employer_dealing_day_rpt import EmployerDealingDayRPT
        from .documents import Documents

        db.create_all(bind=['writeonly'])
        db.session.commit()
        app.logger.debug('All tables are created')
