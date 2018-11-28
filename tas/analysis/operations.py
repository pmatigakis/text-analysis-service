import logging

from tas.analysis.exceptions import UnsupportedContentType
from tas.analysis.processors import HTMLContentProcessor


logger = logging.getLogger(__name__)


class ContentAnalyser(object):
    def __init__(self, keyword_stop_list=None):
        self.keyword_stop_list = keyword_stop_list

        self.__content_type_processors = {
            "html": HTMLContentProcessor(self.keyword_stop_list)
        }

    def _select_content_processor(self, content_type):
        content_type = content_type.lower()

        content_processor = self.__content_type_processors.get(content_type)
        if content_processor is None:
            logger.warning(
                "unsupported request content type: content_type=%s",
                content_type
            )

            raise UnsupportedContentType(content_type)

        return content_processor

    def process_content(self, request):
        content_processor = self._select_content_processor(
            request["content_type"])

        return content_processor.process_content(request["content"])
