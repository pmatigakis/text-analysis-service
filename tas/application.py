from ConfigParser import ConfigParser
import logging
from logging.handlers import RotatingFileHandler

from falcon import API

from tas.resources import ProcessHTML


def load_settings(settings_file):
    config_parser = ConfigParser()

    with open(settings_file) as f:
        config_parser.readfp(f)

    return config_parser


def load_resources(settings, app):
    process_html_resource = ProcessHTML()

    app.add_route("/api/v1/process_html", process_html_resource)


def setup_logging(settings):
    logger = logging.getLogger("tas")

    log_format = "%(asctime)s %(levelname)s [%(process)d:%(thread)d] " \
                 "%(name)s [%(pathname)s:%(funcName)s:%(lineno)d] %(message)s"
    formatter = logging.Formatter(log_format)

    log_levels = {
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "debug": logging.DEBUG
    }

    if settings.getboolean("logging", "enabled"):
        log_level = settings.get("logging", "level")
        log_level = log_levels.get(log_level, logging.INFO)

        filename = settings.get("logging", "filename")
        max_bytes = settings.get("logging", "max_bytes")
        backup_count = settings.get("logging", "backup_count")

        file_handler = RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if settings.getboolean("application", "debug"):
        log_level = logging.DEBUG
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.setLevel(log_level)


def create_app(settings_file):
    settings = load_settings(settings_file)

    app = API()

    setup_logging(settings)
    load_resources(settings, app)

    return app
