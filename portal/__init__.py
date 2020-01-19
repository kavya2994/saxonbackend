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

    http_server = WSGIServer(('0.0.0.0', 811), app)
    http_server.serve_forever()
    return app

