from os import path
from unittest import main
from unittest.mock import patch
import json

from falcon.testing import TestCase

from tas.web.application import create_app
from tas.web import error_codes


page_contents = """
<html>
    <head>
        <meta property="og:title" content="test page title">
        <meta property="og:type" content="article">
        <meta property="og:image" content="https://example.com/image.png">
        <meta property="og:url" content="http://example.com/test_page">
        <meta property="og:description" content="test page description">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:site" content="@topicaxis">
        <meta name="twitter:creator" content="@user">
        <meta name="twitter:title" content="test twitter card">
        <meta name="twitter:description" content="test card description">
        <meta name="twitter:image:src" content="http://example.com/image.png">
        <title>test page</title>
    </head>
    <body>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam
        eget imperdiet ex. Morbi facilisis neque et leo lacinia pulvinar. Duis
        egestas augue a ornare consectetur. Aenean consequat a enim et
        tincidunt. Pellentesque habitant morbi tristique senectus et netus et
        malesuada fames ac turpis egestas. Vestibulum posuere sodales massa,
        vitae lacinia tellus sodales ut. Vivamus rhoncus viverra ante, et
        malesuada lorem. In varius vehicula leo, sit amet lacinia massa
        ultrices vel. Suspendisse nec felis ullamcorper, pellentesque arcu ut,
        elementum erat. Pellentesque habitant morbi tristique senectus et netus
        et malesuada fames ac turpis egestas. Cras rutrum magna eu arcu euismod
        condimentum. Donec pellentesque lectus malesuada arcu feugiat, et
        condimentum mauris tincidunt. Aliquam nec urna felis. Nullam viverra ex
        nec ipsum luctus porta.</p>
    </body>
</html>
"""

request_body = {
    "content_type": "html",
    "content": {
        "url": "http://www.example.com",
        "html": page_contents,
        "headers": {
            "Content-Type": "text/html"
        }
    }
}


class ResourceTestCase(TestCase):
    def setUp(self):
        super(ResourceTestCase, self).setUp()

        settings_file = path.join(
            path.dirname(
                path.abspath(__file__)), "configuration_files", "settings.py")

        self.app = create_app(settings_file)


class ProcessHtmlTests(ResourceTestCase):
    def test_process_html(self):
        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertIn("content", response.json)
        self.assertIn("text", response.json["content"])
        self.assertTrue(
            response.json["content"]["text"].startswith("Lorem ipsum"))
        self.assertIn("title", response.json["content"])
        self.assertEqual("test page", response.json["content"]["title"])

        self.assertIn("keywords", response.json["content"])
        self.assertIsInstance(response.json["content"]["keywords"], dict)

        # TODO: for the moment just check if there are any keywords
        self.assertTrue(len(response.json["content"]["keywords"]) > 0)

        self.assertIn("social", response.json["content"])
        self.assertIn("opengraph", response.json["content"]["social"])
        self.assertIn("twitter", response.json["content"]["social"])

        self.assertDictEqual(
            response.json["content"]["social"]["opengraph"],
            {
                'description': 'test page description',
                'title': 'test page title',
                'url': 'http://example.com/test_page',
                'image': 'https://example.com/image.png',
                'scrape': False,
                'type': 'article'
            }
        )

        self.assertDictEqual(
            response.json["content"]["social"]["twitter"],
            {
                'description': 'test card description',
                'creator': '@user',
                'title': 'test twitter card',
                'site': '@topicaxis',
                'image:src': 'http://example.com/image.png',
                'card': 'summary_large_image'
            }
        )

        self.assertIn("summary", response.json["content"])
        self.assertEqual(
            response.json["content"]["summary"],
            "Suspendisse nec felis ullamcorper, pellentesque arcu ut, "
            "elementum erat.\nDonec pellentesque lectus malesuada arcu "
            "feugiat, et condimentum mauris tincidunt.\nNullam viverra ex "
            "nec ipsum luctus porta."
        )

        self.assertIn("readability_scores", response.json["content"])
        self.assertDictEqual(
            response.json["content"]["readability_scores"],
            {
                "automated_readability_index": 11.0,
                "coleman_liau_index": 15.33,
                "dale_chall_readability_score": 11.27,
                "difficult_words": 55,
                "flesch_kincaid_grade": 8.8,
                "flesch_reading_ease": 46.44,
                "gunning_fog": 23.53333333333333,
                "linsear_write_formula": 2.875,
                "smog_index": 10.2,
                "text_standard": "10th and 11th grade"
            }
        )

        self.assertIn("statistics", response.json["content"])
        self.assertDictEqual(
            response.json["content"]["statistics"],
            {
                "average_sentence_word_count": 9.466666666666667,
                "max_sentence_word_count": 14,
                "mean_sentence_word_count": 9.466666666666667,
                "median_sentence_word_count": 9.0,
                "min_sentence_word_count": 5,
                "sentence_count": 15,
                "sentence_word_count_std": 2.8487814158961995,
                "sentence_word_count_variance": 8.115555555555554,
                "word_count": 142
            }
        )

        self.assertIn("named_entities", response.json["content"])
        self.assertDictEqual(
            response.json["content"]["named_entities"],
            {
                'GPE': sorted([
                    'Morbi', 'Nullam', 'Aliquam', 'Vestibulum', 'Duis',
                    'Aenean', 'Cras', 'Suspendisse', 'Donec', 'Lorem',
                    'Vivamus', 'Pellentesque'
                ])
            }
        )

        self.assertIn("top_image", response.json["content"])
        self.assertEqual(
            response.json["content"]["top_image"],
            "https://example.com/image.png"
        )

        self.assertIn("movies", response.json["content"])
        self.assertEqual(response.json["content"]["movies"], [])

        self.assertIn("images", response.json["content"])
        self.assertEqual(
            response.json["content"]["images"],
            ["https://example.com/image.png"]
        )

        self.assertIn("html", response.json["content"])
        self.assertEqual(response.json["content"]["html"], page_contents)

    @patch("tas.web.routes.ContentAnalyser.process_content")
    def test_content_analyser_raised_unknown_exception(
            self, process_content_mock):
        process_content_mock.side_effect = Exception

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(
            response.json,
            {
                'code': error_codes.TAS_ERROR,
                'description': 'Failed to process content',
                'title': 'Processing error'
            }
        )

    @patch("tas.analysis.operations.HTMLContentProcessor.process_content")
    def test_html_processor_raised_exception(self, process_content_mock):
        process_content_mock.side_effect = Exception

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertEqual(response.status_code, 404)
        self.assertDictEqual(
            response.json,
            {
                'code': error_codes.TAS_ERROR,
                'description': 'Failed to process content',
                'title': 'Processing error'
            }
        )

    def test_html_analysis_request_content_is_invalid(self):
        invalid_request_body = {
            "content_type": "html",
            "content": {
                # "url": "http://www.example.com",
                "html": page_contents,
                "headers": {
                    "Content-Type": "text/html"
                }
            }
        }

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(invalid_request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json,
            {
                'code': error_codes.INVALID_HTML_CONTENT,
                'description': 'The html analysis request contained invalid '
                               'data',
                'title': 'Invalid request body'
            }
        )

    def test_request_content_type_is_not_supported(self):
        invalid_request_body = request_body.copy()
        invalid_request_body["content_type"] = "text/plain"

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(invalid_request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertEqual(response.status_code, 400)

        self.assertDictEqual(
            response.json,
            {
                "code": 1004,
                "description": 'The content type "text/plain" is not '
                               'supported',
                "title": "Invalid request body"
            }
        )

    def test_invalid_request_body_format(self):
        invalid_request_body = request_body.copy()
        del invalid_request_body["content_type"]

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(invalid_request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertEqual(response.status_code, 400)

        self.assertDictEqual(
            response.json,
            {
                "code": 1004,
                "description": "The contents of the request are not in the "
                               "appropriate format",
                "title": "Invalid request body"
            }
        )

    def test_request_body_does_not_have_any_content(self):
        response = self.simulate_post(
            "/api/v1/process", body="")

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json,
            {
                "code": error_codes.EMPTY_REQUEST_BODY,
                "description": "The contents of a web page must be provided",
                "title": "Empty request body"
            }
        )

    def test_request_body_is_not_json(self):
        response = self.simulate_post(
            "/api/v1/process", body="hello world")

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json,
            {
                "code": error_codes.INVALID_REQUEST_BODY,
                "description": "The contents of the request body could not be "
                               "decoded",
                "title": "Invalid request body"
            }
        )


class HealthCheckTests(ResourceTestCase):
    def test_health(self):
        response = self.simulate_get("/service/health", body=page_contents)

        self.assertEqual(response.status_code, 200)

        self.assertDictEqual(
            response.json,
            {
                "result": "ok"
            }
        )


class InformationEndpointTests(ResourceTestCase):
    def test_information(self):
        response = self.simulate_get(
            "/service/information", body=page_contents)

        self.assertEqual(response.status_code, 200)

        self.assertDictEqual(
            response.json,
            {
                "host": "127.0.0.1",
                "port": 8000,
                "service": "tas",
                "version": "0.6.0"
            }
        )


if __name__ == "__main__":
    main()
