import os
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_restx import Api, Resource
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix


APP = None
LOG = logging
WORKER_ID = 0


def uwsgi_friendly_setup(app):
    global WORKER_ID

    try:
        import uwsgi
        WORKER_ID = uwsgi.worker_id()
    except ImportError:
        # During development on local machine, we may use `flask run` command
        # in this case, uwsgi package won't be available and it will throw error
        pass


def get_config_file_path():
    env = os.getenv("BACKEND_ENV", default="development")
    base = os.path.dirname(os.path.abspath(__file__))
    absolute_path = os.path.abspath(os.path.join(base, '..', 'config', env + '.py'))
    return absolute_path


def init_logger(app):
    global LOG
    log_file = os.path.join(app.config['LOG_DIR'], 'backend.log')

    log_level =  app.config['LOG_LEVEL']
    log_format = Formatter(f"[%(asctime)s][worker-{WORKER_ID}][%(levelname)s] %(message)s")

    TWO_MEGABYTE = 2_000_000
    file_handler = RotatingFileHandler(filename=log_file, maxBytes=TWO_MEGABYTE, backupCount=3)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)
    app.logger.addHandler(file_handler)

    LOG = app.logger
    LOG.info('Initialized logger with level %s for worker %s', log_level, WORKER_ID)


def init_cors(app):
    CORS(app=app, origins=app.config['CORS_ORIGIN_WHITELIST'], allow_headers=app.config['CORS_HEADERS'])
    LOG.info('Initialized CORS')


def create_app():
    global APP

    if APP is not None:
        return APP

    APP = Flask(__name__, static_url_path='/static')
    APP.debug = True

    uwsgi_friendly_setup(APP)
    APP.wsgi_app = ProxyFix(APP.wsgi_app, x_for=2)

    config_file_path = get_config_file_path()
    if config_file_path is not None:
        if isinstance(config_file_path, dict):
            APP.config.update(config_file_path)
        elif config_file_path.endswith('.py'):
            APP.config.from_pyfile(config_file_path)

    init_logger(APP)
    try:
        from . import routes, models, services, api, seeds
        api.init_app(APP)
        models.init_app(APP)
        routes.init_app(APP)
        services.init_app(APP)
        seeds.init_app(APP)
        init_cors(APP)
    except Exception as e:
        LOG.warning('An error happened during initializing app components: %s', e)
        raise

    APP.logger.info('App Initialization is finished successfully')
    return APP

