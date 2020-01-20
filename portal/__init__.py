import os
from flask import Flask
from gevent.pywsgi import WSGIServer


def create_app():
    from . import routes, models, services, helpers
    app = Flask(__name__)
    models.init_app(app)
    routes.init_app(app)
    services.init_app(app)
    helpers.init_cors(app)


    app.secret_key = 'random string'
    app.debug = True

    default_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    app.config['DATA_DIR'] = os.getenv("DATA_DIR", default=default_data_dir)

    http_server = WSGIServer(('0.0.0.0', 811), app)
    http_server.serve_forever()
    return app

