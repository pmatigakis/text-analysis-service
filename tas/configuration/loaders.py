from os import path
from types import ModuleType
import logging


class Configuration(dict):
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)

        # TODO: the default configuration should be moved to a separate module
        # and loaded from there instead
        self["CONSUL_HOST"] = None
        self["CONSUL_PORT"] = 8500
        self["CONSUL_SCHEME"] = "http"
        self["CONSUL_VERIFY_SSL"] = True
        self["CONSUL_HEALTH_INTERVAL"] = "10s"
        self["CONSUL_HEALTH_TIMEOUT"] = "5s"
        self["SERVICE_NAME"] = "tas"
        self["SENTRY_DSN"] = None
        self["SENTRY_LOG_LEVEL"] = logging.ERROR

    @classmethod
    def load_from_py(cls, filename):
        filename = filename if path.isabs(filename) else path.abspath(filename)

        settings_module = ModuleType("configuration")
        settings_module.__file__ = filename

        with open(filename) as f:
            exec(compile(f.read(), filename, 'exec'), settings_module.__dict__)

        configuration = cls()

        for key in dir(settings_module):
            if not key.startswith("_"):
                configuration[key] = getattr(settings_module, key)

        return configuration
