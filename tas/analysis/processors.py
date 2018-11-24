from abc import ABCMeta, abstractmethod
import logging

from text_analysis_helpers.html import HtmlAnalyser

from tas.analysis.exceptions import InvalidHTMLContent
from tas.analysis.schemas import WebPageSchema


logger = logging.getLogger(__name__)


class ContentProcessor(object):
    """request content processor base class"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def process_content(self, content):
        """Process the request content

        :param str content: the request content
        :rtype: dict
        :return: the processing result
        """
        pass


class HTMLContentProcessor(ContentProcessor):
    """HTML content processor"""

    def __init__(self, keyword_stop_list=None):
        """Create a new HTMLContentProcessor object

        :param str keyword_stop_list: the keyword stop list to use
        """
        self.keyword_stop_list = keyword_stop_list or "SmartStoplist.txt"

        self.__html_analyser = HtmlAnalyser(self.keyword_stop_list)
        self.__web_page_schema = WebPageSchema()

    def _deserialize_content(self, content):
        result = self.__web_page_schema.load(content)
        if result.errors:
            logger.warning("invalid html contenbt: errors=%s", result.errors)

            raise InvalidHTMLContent(result.errors)

        return result.data

    def process_content(self, content):
        content = self._deserialize_content(content)
        html_analysis_result = self.__html_analyser.analyse(content)

        # we will remote the "_url" key from the opengraph data in order to
        # remain backwards compatible
        opengraph = html_analysis_result.social_network_data.opengraph
        if opengraph is not None and "_url" in opengraph:
            del opengraph["_url"]

        return {
            "content": {
                "text": html_analysis_result.text,
                "title": html_analysis_result.title,
                "keywords": html_analysis_result.keywords,
            },
            "social": {
                "opengraph":
                    html_analysis_result.social_network_data.opengraph,
                "twitter": html_analysis_result.social_network_data.twitter
            }
        }
