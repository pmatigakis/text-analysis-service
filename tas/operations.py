import logging

from tas.exceptions import TASError
from tas.processors import HTMLContentProcessor


logger = logging.getLogger(__name__)


class UnsupportedContentType(TASError):
    def __init__(self, content_type=None):
        super(UnsupportedContentType, self).__init__(content_type)

        self.content_type = content_type


class ContentAnalyser(object):
    def __init__(self, keyword_stop_list=None):
        self.keyword_stop_list = keyword_stop_list

    def _select_content_processor(self, content_type):
        if content_type.startswith("text/html"):
            return HTMLContentProcessor(self.keyword_stop_list)

        logger.warning(
            "unsupported request content type: content_type=%s",
            content_type
        )

        raise UnsupportedContentType(content_type)

    def process_content(self, request):
        content_processor = self._select_content_processor(
            request["content_type"])

        return content_processor.process_content(request["content"])
