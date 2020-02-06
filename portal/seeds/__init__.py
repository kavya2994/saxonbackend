from ..models import db
from ..helpers import isDev



def init_app(app):
    if isDev():
        from .demo import DemoSeeder
        with app.app_context():
            # DemoSeeder(db).run()
            pass
