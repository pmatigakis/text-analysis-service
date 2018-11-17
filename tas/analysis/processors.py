from abc import ABCMeta, abstractmethod
import logging

from bs4 import BeautifulSoup
from opengraph.opengraph import OpenGraph
from newspaper import fulltext
from rake.rake import Rake
from rake.stoplists import get_stoplist_file_path

from tas.analysis.exceptions import HTMLContentProcessorError


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
        keyword_stop_list = keyword_stop_list or "SmartStoplist.txt"
        self.rake = Rake(get_stoplist_file_path(keyword_stop_list))

    def _extract_page_content(self, request_body):
        try:
            content = fulltext(request_body)
        except Exception:
            logger.exception("failed to extract content")
            raise HTMLContentProcessorError()

        return {"text": content}

    def _extract_page_data(self, soup):
        response = {}

        title = soup.find("title")
        # TODO: this is not tested.
        # We need to investigate if it is better to return None instead of an
        # empty string
        response["title"] = title.text if title else ""

        return response

    def _extract_opengraph_data(self, request_body):
        opengraph = OpenGraph()

        opengraph.parser(request_body)

        if opengraph.is_valid():
            del opengraph["_url"]
            return opengraph
        else:
            logger.warning("failed to extract OpenGraph data")
            return None

    def _extract_twitter_card(self, soup):
        card = {}

        for meta in soup.find_all("meta"):
            name = meta.get("name", "")
            if name.startswith("twitter:"):
                items = name.split(":")
                if len(items) < 2:
                    msg = "Invalid twitter card value: twitter_card(%s)"
                    logger.warning(msg, name)
                    continue
                card[":".join(items[1:])] = meta.get("content")

        # if twitter card data could not be extracted then return None instead
        # of an empty dictionary
        if len(card) == 0:
            logger.warning("failed to extract twitter card")
            card = None

        return card

    def _extract_keywords(self, text):
        keywords = self.rake.run(text)

        keywords = {
            keyword: score
            for keyword, score in keywords
        }

        return keywords

    def process_content(self, content):
        soup = BeautifulSoup(content, "html.parser")

        extracted_content = self._extract_page_content(content)
        page_data = self._extract_page_data(soup)
        opengraph_data = self._extract_opengraph_data(content)
        twitter_card = self._extract_twitter_card(soup)

        if (isinstance(extracted_content["text"], str) and
                len(extracted_content["text"]) != 0):
            extracted_content["keywords"] = self._extract_keywords(
                extracted_content["text"])

        content_response = {}
        content_response.update(extracted_content)
        content_response.update(page_data)

        return {
            "content": content_response,
            "social": {
                "opengraph": opengraph_data,
                "twitter": twitter_card
            }
        }