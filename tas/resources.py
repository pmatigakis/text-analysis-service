import logging
import json

from falcon import HTTP_200, HTTP_500, HTTPBadRequest
from goose import Goose
from bs4 import BeautifulSoup
from opengraph import OpenGraph


logger = logging.getLogger(__name__)


class ProcessHTML(object):
    def __init__(self):
        self.goose = Goose()

    def _extract_page_content(self, request_body):
        try:
            article = self.goose.extract(raw_html=request_body)
        except Exception:
            logger.exception("failed to extract content")
            return {"error": "failed to extract content"}

        if article is None:
            content = None
            logger.warning("no content found in page")
        else:
            content = article.cleaned_text

        return {"text": content}

    def _extract_page_data(self, soup):
        response = {}

        title = soup.find("title")
        if title:
            response["title"] = title.text

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

    def on_post(self, req, resp):
        logger.info("processing html content")

        if req.content_length in (None, 0):
            msg = "invalid content length: content_length(%s)"
            logger.warning(msg, req.content_length)
            raise HTTPBadRequest('Invalid request body',
                                 'The content length of the body is not valid')
        elif req.content_length > 250000:
            msg = "very large body: content_length(%s)"
            logger.warning(msg, req.content_length)
            raise HTTPBadRequest('Invalid request body',
                                 'The body is very large')

        body = req.stream.read()
        if not body:
            logger.warning("Empty request body")
            raise HTTPBadRequest('Empty request body',
                                 'The contents of a web page must be provided')

        resp.content_type = "application/json"

        soup = BeautifulSoup(body, "html.parser")

        try:
            content = self._extract_page_content(body)
            page_data = self._extract_page_data(soup)
            opengraph_data = self._extract_opengraph_data(body)
            twitter_card = self._extract_twitter_card(soup)

            resp.status = HTTP_200

            content_response = {}
            content_response.update(content)
            content_response.update(page_data)

            resp.body = json.dumps(
                {
                    "content": content_response,
                    "social": {
                        "opengraph": opengraph_data,
                        "twitter": twitter_card
                    }
                }
            )
        except Exception:
            resp.status = HTTP_500
            resp.body = json.dumps({"error": "failed to process content"})
