import os
from flask import Flask
from flask_restplus import Api, Resource


APP = None

def get_config_file_path():
    env = os.getenv("BACKEND_ENV", default="development")
    base = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.abspath(os.path.join(base, '..', 'config', env + '.py'))
    return absolute_path


def create_app():
    global APP
    APP = Flask(__name__, static_url_path='/static')
    APP.debug = True

    config_file_path = get_config_file_path()
    if config_file_path is not None:
        if isinstance(config_file_path, dict):
            APP.config.update(config_file_path)
        elif config_file_path.endswith('.py'):
            APP.config.from_pyfile(config_file_path)

    from . import routes, models, services, api, seeds
    api.init_app(APP)
    models.init_app(APP)
    routes.init_app(APP)
    services.init_app(APP)
    seeds.init_app(APP)

    return APP

