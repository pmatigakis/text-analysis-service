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
                "html": html_analysis_result.html,
                "title": html_analysis_result.title,
                "keywords": html_analysis_result.keywords,
                "social": {
                    "opengraph":
                        html_analysis_result.social_network_data.opengraph,
                    "twitter": html_analysis_result.social_network_data.twitter
                },
                "summary": html_analysis_result.summary,
                "readability_scores": html_analysis_result.readability_scores,
                "statistics": {
                    # we need to have text-analysis-helpers return these values
                    # as python types instead of numpy types
                    "average_sentence_word_count": float(html_analysis_result.statistics.average_sentence_word_count),  # noqa
                    "max_sentence_word_count": int(html_analysis_result.statistics.max_sentence_word_count),  # noqa
                    "mean_sentence_word_count": float(html_analysis_result.statistics.mean_sentence_word_count),  # noqa
                    "median_sentence_word_count": float(html_analysis_result.statistics.median_sentence_word_count),  # noqa
                    "min_sentence_word_count": int(html_analysis_result.statistics.min_sentence_word_count),  # noqa
                    "sentence_count": int(html_analysis_result.statistics.sentence_count),  # noqa
                    "sentence_word_count_std": float(html_analysis_result.statistics.sentence_word_count_std),  # noqa
                    "sentence_word_count_variance": float(html_analysis_result.statistics.sentence_word_count_variance),  # noqa
                    "word_count": int(html_analysis_result.statistics.word_count)  # noqa
                },
                "named_entities": {
                    entity_type: sorted(list(items))
                    for entity_type, items in
                    html_analysis_result.named_entities.items()
                },
                "top_image": html_analysis_result.top_image,
                "images": list(html_analysis_result.images),
                "movies": html_analysis_result.movies,
            }
        }
