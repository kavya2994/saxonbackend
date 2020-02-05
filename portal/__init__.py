import os
from flask import Flask
from gevent.pywsgi import WSGIServer
from flask_restplus import Api, Resource


def create_app(config=None):
    from . import routes, models, services, helpers, api
    app = Flask(__name__)
    api.init_app(app)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)
    helpers.init_cors(app)


    app.secret_key = 'random string'
    app.debug = True

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    server_address = app.config['SERVER_ADDRESS']
    server_port = app.config['SERVER_PORT']

    http_server = WSGIServer((server_address, server_port), app)
    http_server.serve_forever()
    return app

