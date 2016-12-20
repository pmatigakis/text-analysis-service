import os

from tas.application import create_app


settings_file = os.getenv("TAS_SETTINGS")

if settings_file is None:
    print("The environment variable TAS_SETTINGS is not set")
    exit(1)

app = create_app(settings_file)
