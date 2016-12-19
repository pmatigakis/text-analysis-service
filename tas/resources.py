import json

from falcon import HTTP_200, HTTPBadRequest
from goose import Goose
from bs4 import BeautifulSoup


class ProcessHTML(object):
    def __init__(self):
        self.goose = Goose()

    def _extract_page_content(self, request_body):
        try:
            article = self.goose.extract(raw_html=request_body)
        except Exception:
            return {"error": "failed to extract content"}

        if article is None:
            content = None
        else:
            content = article.cleaned_text

        return {"text": content}

    def _extract_page_data(self, request_body):
        soup = BeautifulSoup(request_body, "html.parser")

        response = {}

        title = soup.find("title")
        if title:
            response["title"] = title.text
            response["content-length"] = len(request_body)

        return response

    def on_post(self, req, resp):
        if req.content_length in (None, 0):
            raise HTTPBadRequest('Invalid request body',
                                 'The content length of the body is not valid')
        elif req.content_length > 250000:
            raise HTTPBadRequest('Invalid request body',
                                 'The body is very large')

        body = req.stream.read()
        if not body:
            raise HTTPBadRequest('Empty request body',
                                 'The contents of a web page must be provided')

        resp.content_type = "application/json"

        try:
            content = self._extract_page_content(body)
            page_data = self._extract_page_data(body)

            resp.status = HTTP_200

            content_response = {}
            content_response.update(content)
            content_response.update(page_data)

            resp.body = json.dumps(
                {
                    "content": content_response
                }
            )
        except Exception:
            resp.status = HTTP_200
            resp.body = json.dumps({"error": "failed to process content"})
