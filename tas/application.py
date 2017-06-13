import logging
from logging.handlers import RotatingFileHandler

from falcon import API
from raven.handlers.logging import SentryHandler

from tas.configuration.loaders import Configuration
from tas.routes import load_resources


def _setup_logging(configuration):
    logger = logging.getLogger("tas")
    logger.handlers = []

    log_format = "%(asctime)s %(levelname)s [%(process)d:%(thread)d] " \
                 "%(name)s [%(pathname)s:%(funcName)s:%(lineno)d] %(message)s"
    formatter = logging.Formatter(log_format)

    log_level = configuration["LOG_LEVEL"]

    if configuration["DEBUG"]:
        log_level = logging.DEBUG

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if configuration["LOG_FILE"] is not None:
        file_handler = RotatingFileHandler(
            configuration["LOG_FILE"],
            maxBytes=configuration["LOG_FILE_MAX_SIZE"],
            backupCount=configuration["LOG_FILE_COUNT"]
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    for log_handler in configuration["LOG_HANDLERS"]:
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

    logger.setLevel(log_level)


def _initialize_sentry(configuration):
    handler = SentryHandler(configuration["SENTRY_DSN"])
    handler.setLevel(configuration["SENTRY_LOG_LEVEL"])

    logger = logging.getLogger("tas")
    logger.addHandler(handler)


def create_app(settings_file):
    configuration = Configuration.load_from_py(settings_file)

    app = API()

    _setup_logging(configuration)

    if configuration["SENTRY_DSN"]:
        _initialize_sentry(configuration)

    load_resources(configuration, app)

    return app
