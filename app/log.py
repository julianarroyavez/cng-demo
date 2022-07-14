import logging

from app import config

logging.basicConfig(level=config.LOG_LEVEL)

LOG = logging.getLogger("API")
LOG.propagate = False

PAYTM_LOG = logging.getLogger("PAYTM")
PAYTM_LOG.propagate = False

WALLET_LOG = logging.getLogger("WALLET")
WALLET_LOG.propagate = False

PEEWEE_LOG = logging.getLogger('peewee')
PEEWEE_LOG.setLevel(config.DB_LOG_LEVEL)

LOG_FORMAT = "[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] %(message)s"

if config.APP_ENV == "prod":
    from logging.handlers import TimedRotatingFileHandler

    file_handler = TimedRotatingFileHandler("{}/backend_server.log".format(config.LOG_DIRECTORY), "h", 24, 10)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    LOG.addHandler(file_handler)
    PAYTM_LOG.addHandler(file_handler)
    WALLET_LOG.addHandler(file_handler)
    PEEWEE_LOG.addHandler(file_handler)

else:
    from logging.handlers import TimedRotatingFileHandler

    stream_handler = TimedRotatingFileHandler("{}/backend_server.log".format(config.LOG_DIRECTORY), "m", 70, 10)
    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler.setFormatter(formatter)
    LOG.addHandler(stream_handler)
    PAYTM_LOG.addHandler(stream_handler)
    WALLET_LOG.addHandler(stream_handler)
    PEEWEE_LOG.addHandler(stream_handler)


def get_logger():
    return LOG
