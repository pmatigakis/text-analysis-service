import logging

from falcon import API

from tas.resources import ProcessHTML, Health, Information
from tas.configuration.loaders import Configuration


def load_resources(configuration, app):
    process_html_resource = ProcessHTML(
        keyword_stop_list=configuration["KEYWORD_STOP_LIST"]
    )

    app.add_route("/api/v1/process", process_html_resource)
    app.add_route("/service/health", Health())
    app.add_route("/service/information", Information(configuration))


def setup_logging(configuration):
    logger = logging.getLogger("tas")
    logger.handlers = []

    log_format = "%(asctime)s %(levelname)s [%(process)d:%(thread)d] " \
                 "%(name)s [%(pathname)s:%(funcName)s:%(lineno)d] %(message)s"
    formatter = logging.Formatter(log_format)

    log_level = configuration["LOG_LEVEL"]

    if configuration["DEBUG"]:
        log_level = logging.DEBUG
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    logger.setLevel(log_level)

    for log_handler in configuration["LOG_HANDLERS"]:
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)


def create_app(settings_file):
    configuration = Configuration.load_from_py(settings_file)

    app = API()

    if configuration["ENABLE_LOGGING"]:
        setup_logging(configuration)

    load_resources(configuration, app)

    return app
