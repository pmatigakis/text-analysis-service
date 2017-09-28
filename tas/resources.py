import logging
import json
import time

from falcon import HTTP_200, HTTPBadRequest, HTTPNotFound

from tas import error_codes, __VERSION__
from tas.processors import HTMLContentProcessor, HTMLContentProcessorError
from tas.metrics.utils import metrics


PROCESS_HTML_REQUEST_COUNTER = "topicaxis.tas.processhtml.request"
PROCESS_HTML_ERROR_COUNTER = "topicaxis.tas.processhtml.error"
PROCESS_HTML_SUCCESS_COUNTER = "topicaxis.tas.processhtml.success"
PROCESS_HTML_EXECUTION_TIME = "topicaxis.tas.processhtml.execution"


logger = logging.getLogger(__name__)


class ProcessHTML(object):
    def __init__(self, keyword_stop_list=None):
        self.keyword_stop_list = keyword_stop_list

    def _is_valid_request_body(self, request_body):
        return "content_type" in request_body and "content" in request_body

    def _is_supported_content_type(self, request_body_content_type):
        # only text/html is supported for the moment
        return request_body_content_type.startswith("text/html")

    def _select_content_processor(self, request_content_type):
        if request_content_type.startswith("text/html"):
            return HTMLContentProcessor(self.keyword_stop_list)

        logger.warning(
            "unsupported request content type: content_type=%s",
            request_content_type
        )

        # this content type is not supported
        raise HTTPBadRequest(
            title='Invalid request body',
            description='The content type "{}" is not supported'.format(
                request_content_type),
            code=error_codes.INVALID_REQUEST_BODY
        )

    def on_post(self, req, resp):
        request_start_time = time.perf_counter()

        logger.info("processing html content")
        metrics.incr(PROCESS_HTML_REQUEST_COUNTER)

        body = req.stream.read()
        if not body:
            logger.warning("Empty request body")
            metrics.incr(PROCESS_HTML_ERROR_COUNTER)

            raise HTTPBadRequest(
                title='Empty request body',
                description='The contents of a web page must be provided',
                code=error_codes.EMPTY_REQUEST_BODY
            )

        try:
            body = json.loads(body.decode("utf8"))
        except ValueError:
            logger.exception("failed to decode request body")
            metrics.incr(PROCESS_HTML_ERROR_COUNTER)

            raise HTTPBadRequest(
                title='Invalid request body',
                description='The contents of the request body could not be '
                            'decoded',
                code=error_codes.INVALID_REQUEST_BODY
            )

        if not self._is_valid_request_body(body):
            logger.warning("invalid processing request body")
            metrics.incr(PROCESS_HTML_ERROR_COUNTER)

            raise HTTPBadRequest(
                title='Invalid request body',
                description='The contents of the request are not in the '
                            'appropriate format',
                code=error_codes.INVALID_REQUEST_BODY
            )

        if not self._is_supported_content_type(body["content_type"]):
            logger.warning(
                "unsupported content type: content_type=%s",
                body["content_type"]
            )
            metrics.incr(PROCESS_HTML_ERROR_COUNTER)

            raise HTTPBadRequest(
                title='Invalid request body',
                description='The content type "{}" is not supported'.format(
                    body["content_type"]),
                code=error_codes.INVALID_REQUEST_BODY
            )

        content_processor = self._select_content_processor(
            body["content_type"])

        try:
            processing_result = content_processor.process_content(
                body["content"])
        except HTMLContentProcessorError:
            logger.warning("failed to extract content ")
            metrics.incr(PROCESS_HTML_ERROR_COUNTER)

            raise HTTPNotFound(
                title="Processing error",
                description="Failed to process content",
                code=error_codes.TAS_ERROR
            )
        except Exception:
            logger.exception("failed to process content")
            metrics.incr(PROCESS_HTML_ERROR_COUNTER)

            raise HTTPNotFound(
                title="Processing error",
                description="Failed to process content",
                code=error_codes.TAS_ERROR
            )

        resp.status = HTTP_200
        resp.content_type = "application/json"
        resp.body = json.dumps(processing_result)

        execution_time = time.perf_counter() - request_start_time
        log_msg = "page processing request executed: " \
                  "execution_time({execution_time})"
        logger.info(log_msg.format(
            execution_time=execution_time
        ))

        metrics.incr(PROCESS_HTML_SUCCESS_COUNTER)
        # the timing must be in milliseconds
        metrics.timing(PROCESS_HTML_EXECUTION_TIME, execution_time * 1000)


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
