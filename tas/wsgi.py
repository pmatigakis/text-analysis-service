from os import getcwd, path

from tas.application import create_app


def wsgi_app():
    settings_file = path.join(getcwd(), "settings.py")

    return create_app(settings_file)
