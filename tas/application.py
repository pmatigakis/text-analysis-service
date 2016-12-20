from ConfigParser import ConfigParser

from falcon import API

from tas.resources import ProcessHTML


def load_settings(settings_file):
    config_parser = ConfigParser()

    with open(settings_file) as f:
        config_parser.readfp(f)

    return config_parser


def load_resources(settings, app):
    process_html_resource = ProcessHTML()

    app.add_route("/api/v1/process_html", process_html_resource)


def create_app(settings_file):
    settings = load_settings(settings_file)

    app = API()

    load_resources(settings, app)

    return app
