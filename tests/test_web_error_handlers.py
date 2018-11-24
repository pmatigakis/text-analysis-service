from unittest import TestCase, main

from falcon import HTTPNotFound

from tas.analysis.exceptions import HTMLContentProcessorError
from tas.web.error_codes import TAS_ERROR, HTML_CONTENT_PROCESSING_ERROR
from tas.web.error_handlers import ProcessHTMLErrorHandler


class ProcessHTMLErrorHandlerTests(TestCase):
    def test_handle_unknown_error(self):
        error_handler = ProcessHTMLErrorHandler()

        exception = error_handler.handle_exception(Exception())

        self.assertIsInstance(exception, HTTPNotFound)
        self.assertEqual(exception.code, TAS_ERROR)
        self.assertEqual(exception.description, "Failed to process content")

    def test_handle_html_content_processor_error(self):
        error_handler = ProcessHTMLErrorHandler()

        exception = error_handler.handle_exception(HTMLContentProcessorError())

        self.assertIsInstance(exception, HTTPNotFound)
        self.assertEqual(exception.code, HTML_CONTENT_PROCESSING_ERROR)
        self.assertEqual(exception.description, "Failed to process content")


if __name__ == "__main__":
    main()
