from os import path
from unittest import main

from falcon.testing import TestCase
from mock import patch
from goose import Goose
from opengraph import OpenGraph

from tas.application import create_app
from tas.resources import ProcessHTML


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
            "/api/v1/process_html", body=page_contents)

        self.assertIn("content", response.json)
        self.assertIn("text", response.json["content"])
        self.assertTrue(
            response.json["content"]["text"].startswith("Lorem ipsum"))
        self.assertIn("title", response.json["content"])
        self.assertEqual("test page", response.json["content"]["title"])

        self.assertIn("keywords", response.json["content"])
        self.assertIsInstance(response.json["content"]["keywords"], list)

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

    @patch.object(Goose, "extract")
    def test_failed_to_extract_page_content(self, extract_mock):
        extract_mock.side_effect = Exception()

        response = self.simulate_post(
            "/api/v1/process_html", body=page_contents)

        self.assertIn("content", response.json)
        self.assertDictEqual(
            response.json["content"],
            {'error': 'failed to extract content', 'title': 'test page'}
        )

        self.assertNotIn("keywords", response.json["content"])

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

    @patch.object(Goose, "extract")
    def test_page_does_not_have_any_content(self, extract_mock):
        extract_mock.return_value = None

        response = self.simulate_post(
            "/api/v1/process_html", body=page_contents)

        self.assertIn("content", response.json)
        self.assertDictEqual(
            response.json["content"],
            {'text': None, 'title': 'test page'}
        )

    @patch.object(OpenGraph, "is_valid")
    def test_failed_to_extract_opengraph_data(self, is_valid_mock):
        is_valid_mock.return_value = False

        response = self.simulate_post(
            "/api/v1/process_html", body=page_contents)

        self.assertIn("social", response.json)
        self.assertIn("opengraph", response.json["social"])

        self.assertIsNone(response.json["social"]["opengraph"])

    @patch.object(ProcessHTML, "_extract_page_content")
    def test_failed_to_extract_opengraph_data_when_exception_is_raised(
            self, extract_page_content_mock):
        extract_page_content_mock.side_effect = Exception

        response = self.simulate_post(
            "/api/v1/process_html", body=page_contents)

        self.assertDictEqual(
            response.json,
            {'error': 'failed to process content'}
        )

    def test_fail_to_process_page_when_content_length_is_0(self):
        response = self.simulate_post(
            "/api/v1/process_html", body="")

        self.assertDictEqual(
            response.json,
            {
                'description': 'The content length of the body is not valid',
                'title': 'Invalid request body'
            }
        )

    def test_fail_to_process_page_when_content_length_is_large(self):
        response = self.simulate_post(
            "/api/v1/process_html",
            body="a" * 300000,
        )

        self.assertDictEqual(
            response.json,
            {
                'description': 'The body is very large',
                'title': 'Invalid request body'
            }
        )

    @patch.object(ProcessHTML, "_extract_keywords")
    def test_failed_to_extract_keywords_when_exception_is_raised(
            self, extract_keywords_mock):
        extract_keywords_mock.side_effect = Exception

        response = self.simulate_post(
            "/api/v1/process_html", body=page_contents)

        self.assertDictEqual(
            response.json,
            {'error': 'failed to process content'}
        )


if __name__ == "__main__":
    main()
