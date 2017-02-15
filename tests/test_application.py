from os import path
from unittest import TestCase, main

from falcon import API

from tas.application import create_app


class ApplicationCreationTests(TestCase):
    def test_create_app(self):
        settings_file = path.join(
            path.dirname(
                path.abspath(__file__)), "configuration_files", "settings.py")

        app = create_app(settings_file)

        self.assertIsNotNone(app)
        self.assertIsInstance(app, API)


if __name__ == "__main__":
    main()
