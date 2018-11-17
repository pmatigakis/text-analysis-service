import logging.config

from falcon import API
from metricslib.utils import configure_metrics_from_dict

from tas.configuration.loaders import Configuration
from tas.web.routes import load_resources


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
