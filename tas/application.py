import logging
from logging.handlers import RotatingFileHandler

from falcon import API

from tas.resources import ProcessHTML
from tas.configuration.loaders import Configuration


def load_resources(configuration, app):
    process_html_resource = ProcessHTML()

    app.add_route("/api/v1/process_html", process_html_resource)


def setup_logging(configuration):
    logger = logging.getLogger("tas")

    log_format = "%(asctime)s %(levelname)s [%(process)d:%(thread)d] " \
                 "%(name)s [%(pathname)s:%(funcName)s:%(lineno)d] %(message)s"
    formatter = logging.Formatter(log_format)

    if configuration["ENABLE_LOGGING"]:
        log_level = configuration["LOG_LEVEL"]

        filename = configuration["LOG_FILE"]
        max_bytes = configuration["LOG_MAX_BYTES"]
        backup_count = configuration["LOG_BACKUP_COUNT"]

        file_handler = RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if configuration["DEBUG"]:
        log_level = logging.DEBUG
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.setLevel(log_level)


def create_app(settings_file):
    configuration = Configuration.load_from_py(settings_file)

    app = API()

    setup_logging(configuration)
    load_resources(configuration, app)

    return app
