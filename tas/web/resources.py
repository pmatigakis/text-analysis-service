import logging
import json
import time

from falcon import HTTP_200, HTTPBadRequest, HTTPNotFound
import jsonschema
from metricslib.decorators import capture_metrics

from tas import __VERSION__
from tas.web import error_codes
from tas.web.error_handlers import ProcessHTMLErrorHandler
from tas.exceptions import TASError
from tas.web.schemas import process_html_payload_schema


PROCESS_HTML_REQUEST_COUNTER = "topicaxis.tas.processhtml.request"
PROCESS_HTML_ERROR_COUNTER = "topicaxis.tas.processhtml.error"
PROCESS_HTML_SUCCESS_COUNTER = "topicaxis.tas.processhtml.success"
PROCESS_HTML_EXECUTION_TIME = "topicaxis.tas.processhtml.execution"


logger = logging.getLogger(__name__)


class ProcessHTML(object):
    def __init__(self, content_analyser):
        self.content_analyser = content_analyser

        self._error_handler = ProcessHTMLErrorHandler()

    @staticmethod
    def _is_valid_request_body(request_body):
        try:
            jsonschema.validate(request_body, process_html_payload_schema)
        except jsonschema.ValidationError:
            logger.exception("invalid process_html request payload")
            return False

        return True

    def _extract_content_from_request(self, request):
        content = request.stream.read()
        if not content:
            logger.warning("Empty request body")

            raise HTTPBadRequest(
                title='Empty request body',
                description='The contents of a web page must be provided',
                code=error_codes.EMPTY_REQUEST_BODY
            )

        try:
            content = json.loads(content.decode("utf8"))
        except ValueError:
            logger.exception("failed to decode request body")

            raise HTTPBadRequest(
                title='Invalid request body',
                description='The contents of the request body could not be '
                            'decoded',
                code=error_codes.INVALID_REQUEST_BODY
            )

        if not self._is_valid_request_body(content):
            logger.warning("invalid processing request body")

            raise HTTPBadRequest(
                title='Invalid request body',
                description='The contents of the request are not in the '
                            'appropriate format',
                code=error_codes.INVALID_REQUEST_BODY
            )

        return content

    @capture_metrics(
        request_metric=PROCESS_HTML_REQUEST_COUNTER,
        error_metric=PROCESS_HTML_ERROR_COUNTER,
        success_metric=PROCESS_HTML_SUCCESS_COUNTER,
        execution_time_metric=PROCESS_HTML_EXECUTION_TIME
    )
    def on_post(self, req, resp):
        request_start_time = time.perf_counter()

        logger.info("processing html content")

        content = self._extract_content_from_request(req)

        try:
            processing_result = self.content_analyser.process_content(content)
        except TASError as e:
            logger.warning("TAS failed to failed to process content")

            raise self._error_handler.handle_exception(e) from e
        except Exception as e:
            logger.exception("failed to process content")

            raise HTTPNotFound(
                title="Processing error",
                description="Failed to process content",
                code=error_codes.TAS_ERROR
            ) from e

        resp.status = HTTP_200
        resp.content_type = "application/json"
        resp.body = json.dumps(processing_result)

        execution_time = time.perf_counter() - request_start_time
        log_msg = "page processing request executed: " \
                  "execution_time({execution_time})"
        logger.info(log_msg.format(
            execution_time=execution_time
        ))


class Health(object):
    def on_get(self, req, resp):
        logger.info("health check requested")

        resp.status = HTTP_200
        resp.content_type = "application/json"
        resp.body = json.dumps({"result": "ok"})


class Information(object):
    def __init__(self, configuration):
        self.configuration = configuration

    def on_get(self, req, resp):
        logger.info("service information requested")

        resp.status = HTTP_200
        resp.content_type = "application/json"

        response = {
            "service": "tas",
            "version": __VERSION__,
            "host": self.configuration.get("HOST"),
            "port": self.configuration.get("PORT")
        }

        resp.body = json.dumps(response)
