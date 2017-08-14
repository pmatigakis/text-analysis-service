import logging.config

from falcon import API
from raven.handlers.logging import SentryHandler

from tas.configuration.loaders import Configuration
from tas.routes import load_resources


def _setup_logging(configuration):
    log_config = configuration.get("LOGGING")

    if log_config is not None:
        logging.config.dictConfig(log_config)


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
