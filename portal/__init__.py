import os
from flask import Flask
from flask_restplus import Api, Resource


def get_config_file_path():
    env = os.getenv("FLASK_ENV", default="development")
    base = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.abspath(os.path.join(base, '..', 'config', env + '.py'))
    return absolute_path

def create_app():
    app = Flask(__name__, static_url_path='/static')
    app.debug = True

    config_file_path = get_config_file_path()
    if config_file_path is not None:
        if isinstance(config_file_path, dict):
            app.config.update(config_file_path)
        elif config_file_path.endswith('.py'):
            app.config.from_pyfile(config_file_path)


    from . import routes, models, services, helpers, api, seeds
    api.init_app(app)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)
    helpers.init_cors(app)
    seeds.init_app(app)

    return app

