from ... import LOG


def dummy_job(app):
    LOG.info("A scheduled dummy background job was executed")
