from ..models import db
from ..helpers import isDev



def init_app(app):
    with app.app_context():
        from .production import ProductionSeeder
        ProductionSeeder(db).run()

        if not isDev():
            return

        from .development import DevelopmentSeeder
        DevelopmentSeeder(db).run()
