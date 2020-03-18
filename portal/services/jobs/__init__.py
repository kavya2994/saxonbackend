import atexit
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from ... import LOG


def init_jobs(app):
    with app.app_context():
        scheduler = BackgroundScheduler()

        _add_jobs(scheduler, app)

        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())


def _add_jobs(scheduler, app):
    from .form_reminder import send_form_reminder
    Thread(target=send_form_reminder, args=(app,)).start()
    scheduler.add_job(func=send_form_reminder, args=(app,), trigger="interval", days=1)
    LOG.info('Initialized send_form_reminder background job')

    # from .dummy_job import dummy_job
    # scheduler.add_job(func=dummy_job, trigger="interval", minutes=1)
    # LOG.info('Initialized dummy_job background job')

    from .create_accounts import create_accounts
    print("creating accounts")
    LOG.info("creating accounts")
    # create_accounts(app)
    Thread(target=create_accounts, args=(app,)).start()
    scheduler.add_job(func=create_accounts, args=(app,), trigger="interval", days=1)
    LOG.info('Initialized create accounts background job')
