import threading

from ..models import db
from ..helpers import isDev


def init_app(app):
    with app.app_context():
        from .production import ProductionSeeder
        ProductionSeeder(db).run()

        # if not isDev():
        #     return

        from .development import DevelopmentSeeder
        DevelopmentSeeder(db).run()

        from .create_folder_structure import create_folders
        create_folders()

        # from .create_users import scheduler
        # threading.Thread(target=scheduler, args=(app,)).start()

    app.logger.info('Initialized seeding')
