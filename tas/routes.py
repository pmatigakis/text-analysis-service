import logging

from tas.resources import ProcessHTML, Health, Information


logger = logging.getLogger(__name__)


def load_resources(configuration, app):
    logger.debug("loading endpoint routes")

    process_html_resource = ProcessHTML(
        keyword_stop_list=configuration["KEYWORD_STOP_LIST"]
    )

    app.add_route("/api/v1/process", process_html_resource)
    app.add_route("/service/health", Health())
    app.add_route("/service/information", Information(configuration))
