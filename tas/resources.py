import json

from falcon import HTTP_200, HTTPBadRequest
from goose import Goose
from bs4 import BeautifulSoup


class ProcessText(object):
    def __init__(self):
        self.goose = Goose()

    def _extract_content(self, content):
        try:
            article = self.goose.extract(raw_html=content)
        except Exception:
            return {"error": "failed to extract content"}

        response = {}

        if article is None:
            response["text"] = None
        else:
            response["text"] = article.cleaned_text

        soup = BeautifulSoup(content, "html.parser")

        title = soup.find("title")
        if title:
            response["title"] = title.text

        return response

    def on_post(self, req, resp):
        extract_html = req.get_param_as_bool("extract_html") or False

        if req.content_length in (None, 0):
            raise HTTPBadRequest('Invalid request body',
                                 'The content length of the body is not valid')
        elif req.content_length > 250000:
            raise HTTPBadRequest('Invalid request body',
                                 'The body is very large')
        elif req.content_type != "application/json":
            raise HTTPBadRequest('Invalid request body',
                                 'Body content type is not JSON')

        body = req.stream.read()
        if not body:
            raise HTTPBadRequest('Empty request body',
                                 'A valid JSON document is required.')

        try:
            body = json.loads(body)
        except Exception:
            raise HTTPBadRequest('Invalid request body',
                                 'Failed to decode body')

        response = {}

        if extract_html:
            try:
                response["content"] = self._extract_content(body["content"])
            except Exception:
                response["content"] = {"error": "failed to process content"}

        resp.body = json.dumps({"result": response})
        resp.status = HTTP_200
        resp.content_type = "application/json"
