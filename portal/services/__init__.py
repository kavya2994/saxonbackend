from .jobs import init_jobs


def init_app(app):
    app.logger.info('Initialized services')
    init_jobs(app)
