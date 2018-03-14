from os import path
from unittest import main
from unittest.mock import patch
import json

from falcon.testing import TestCase
from opengraph.opengraph import OpenGraph

from tas.application import create_app
from tas.resources import HTMLContentProcessor
from tas import error_codes
from tas.processors import HTMLContentProcessorError


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
    "content_type": "text/html",
    "content": page_contents
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

        self.assertIn("social", response.json)
        self.assertIn("opengraph", response.json["social"])
        self.assertIn("twitter", response.json["social"])

        self.assertDictEqual(
            response.json["social"]["opengraph"],
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
            response.json["social"]["twitter"],
            {
                'description': 'test card description',
                'creator': '@user',
                'title': 'test twitter card',
                'site': '@topicaxis',
                'image:src': 'http://example.com/image.png',
                'card': 'summary_large_image'
            }
        )

    @patch("tas.processors.fulltext")
    def test_failed_to_extract_page_content_newspaper_raised_exception(
            self, fulltext_mock):
        fulltext_mock.side_effect = Exception()

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

    @patch("tas.resources.HTMLContentProcessor.process_content")
    def test_failed_to_extract_page_content(
            self, process_content_mock):
        process_content_mock.side_effect = HTMLContentProcessorError()

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

    @patch("tas.processors.fulltext")
    def test_page_does_not_have_any_content(self, fulltext_mock):
        fulltext_mock.return_value = None

        response = self.simulate_post(
            "/api/v1/process", body=page_contents)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            response.json,
            {
                "code": 1004,
                "description": "The contents of the request body could not "
                               "be decoded",
                "title": "Invalid request body"
            }
        )

    @patch.object(OpenGraph, "is_valid")
    def test_failed_to_extract_opengraph_data(self, is_valid_mock):
        is_valid_mock.return_value = False

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertIn("social", response.json)
        self.assertIn("opengraph", response.json["social"])

        self.assertIsNone(response.json["social"]["opengraph"])

    @patch.object(HTMLContentProcessor, "_extract_page_content")
    def test_failed_to_extract_opengraph_data_when_exception_is_raised(
            self, extract_page_content_mock):
        extract_page_content_mock.side_effect = Exception

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertDictEqual(
            response.json,
            {
                'code': 1003,
                'description': 'Failed to process content',
                'title': 'Processing error'

            }
        )

    @patch.object(HTMLContentProcessor, "_extract_keywords")
    def test_failed_to_extract_keywords_when_exception_is_raised(
            self, extract_keywords_mock):
        extract_keywords_mock.side_effect = Exception

        response = self.simulate_post(
            "/api/v1/process",
            body=json.dumps(request_body),
            headers={
                "Content-Type": "application/json"
            }
        )

        self.assertDictEqual(
            response.json,
            {
                'description': 'Failed to process content',
                'title': 'Processing error',
                'code': 1003
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
                "version": "0.5.0"
            }
        )


if __name__ == "__main__":
    main()
