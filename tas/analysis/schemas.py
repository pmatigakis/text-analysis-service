from marshmallow import Schema, post_load
from marshmallow.fields import Dict, String, Url
from text_analysis_helpers.models import WebPage


class WebPageSchema(Schema):
    url = Url(required=True, allow_none=False)
    html = String(required=True)
    headers = Dict(required=True)

    @post_load()
    def make_web_page(self, data):
        return WebPage(**data)
