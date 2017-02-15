from os import path
from types import ModuleType


class Configuration(dict):
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
