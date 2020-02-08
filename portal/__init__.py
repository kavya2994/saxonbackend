import os
from flask import Flask
from flask_restplus import Api, Resource


def create_app(config=None):
    app = Flask(__name__, static_url_path='/static')
    app.secret_key = 'random string'
    app.debug = True

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    from . import routes, models, services, helpers, api, seeds
    api.init_app(app)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)
    helpers.init_cors(app)
    seeds.init_app(app)

    return app

