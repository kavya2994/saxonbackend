from .index import index_blueprint
from .user import user_blueprint
from .auth import auth_blueprint
from .enrollment import enrollment_blueprint
from .file import file_blueprint
from .aux import aux_blueprint


def init_app(app):
    app.register_blueprint(index_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(enrollment_blueprint)
    app.register_blueprint(file_blueprint)
    app.register_blueprint(aux_blueprint)
    pass
