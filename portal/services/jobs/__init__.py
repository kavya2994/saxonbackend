import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from ... import LOG


def init_jobs(app):
    with app.app_context():
        scheduler = BackgroundScheduler()

        _add_jobs(scheduler)

        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())


def _add_jobs(scheduler):
    from .form_reminder import send_form_reminder
    scheduler.add_job(func=send_form_reminder, trigger="interval", days=1)
    LOG.info('Initialized send_form_reminder background job')

    # from .dummy_job import dummy_job
    # scheduler.add_job(func=dummy_job, trigger="interval", minutes=1)
    # LOG.info('Initialized dummy_job background job')
