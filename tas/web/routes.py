import logging

from tas.analysis.operations import ContentAnalyser
from tas.web.resources import ProcessHTML, Health, Information


logger = logging.getLogger(__name__)


def load_resources(configuration, app):
    logger.debug("loading endpoint routes")

    content_analyser = ContentAnalyser(configuration["KEYWORD_STOP_LIST"])
    process_html_resource = ProcessHTML(content_analyser)

    app.add_route("/api/v1/process", process_html_resource)
    app.add_route("/service/health", Health())
    app.add_route("/service/information", Information(configuration))
