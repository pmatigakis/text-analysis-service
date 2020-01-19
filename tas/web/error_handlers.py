from abc import ABCMeta, abstractmethod
import logging

from tas.web import error_codes
from tas.analysis.exceptions import (
    HTMLContentProcessorError, InvalidHTMLContent
)

from falcon import HTTPBadRequest, HTTPNotFound


logger = logging.getLogger(__name__)


class ErrorHandlerBase(metaclass=ABCMeta):
    """Base class for all REST API error handlers"""

    def __init__(self, error_handlers):
        """Create an error handler object

        :param dict[TASError, (TASError) -> HTTPError] error_handlers: the
            supported errors
        """
        self.error_handlers = error_handlers

    @abstractmethod
    def handle_unknown_exception(self, exception):
        """Handle an unknown exception

        :param TASError exception: the unknown exception
        :rtype: HTTPError
        :return: the falcon exception to raise
        """
        pass

    def handle_exception(self, exception):
        """Handle this exception

        :param TASError exception: the exception to handle
        :rtype: HTTPError
        :return: the falcon exception to raise
        """
        error_handler = self.error_handlers.get(type(exception))

        if error_handler is not None:
            return error_handler(exception)
        else:
            return self.handle_unknown_exception(exception)


class ProcessHTMLErrorHandler(ErrorHandlerBase):
    """Error handler for the process html endpoint"""

    def __init__(self):
        error_handlers = {
            HTMLContentProcessorError:
                self._handle_html_content_processor_error,
            InvalidHTMLContent: self._handle_invalid_html_content_error
        }

        super(ProcessHTMLErrorHandler, self).__init__(error_handlers)

    def _handle_invalid_html_content_error(self, exception):
        logger.warning("invalid html content: errors=%s", exception.errors)

        return HTTPBadRequest(
            title='Invalid request body',
            description="The html analysis request contained invalid data",
            code=error_codes.INVALID_HTML_CONTENT
        )

    def _handle_html_content_processor_error(self, exception):
        logger.warning("failed to extract content ")

        return HTTPNotFound(
            title="Processing error",
            description="Failed to process content",
            code=error_codes.HTML_CONTENT_PROCESSING_ERROR
        )

    def handle_unknown_exception(self, exception):
        logger.error("failed to process content: exception=%s", exception)

        return HTTPNotFound(
            title="Processing error",
            description="Failed to process content",
            code=error_codes.TAS_ERROR
        )
