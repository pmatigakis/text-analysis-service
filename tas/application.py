import logging.config

from falcon import API

from tas.configuration.loaders import Configuration
from tas.routes import load_resources
from tas.metrics.utils import configure_metrics_from_dict


def _setup_logging(configuration):
    log_config = configuration.get("LOGGING")

    if log_config is not None:
        logging.config.dictConfig(log_config)


def create_app(settings_file):
    configuration = Configuration.load_from_py(settings_file)

    app = API()

    _setup_logging(configuration)

    load_resources(configuration, app)
    configure_metrics_from_dict(configuration)

    return app
