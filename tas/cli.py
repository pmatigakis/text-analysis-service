from os import getcwd, path
from argparse import ArgumentParser

from tas.configuration.loaders import Configuration
from tas.servers import Server
from tas.application import create_app


def run(args):
    settings_file = path.join(getcwd(), "settings.py")

    configuration = Configuration.load_from_py(settings_file)

    worker_max_requests = configuration.get(
        "WORKER_MAX_REQUESTS", 100)
    worker_request_jitter = configuration.get(
        "WORKER_MAX_REQUESTS_JITTER", 10)

    options = {
        "preload_app": False,
        "bind": "{host}:{port}".format(
            host=configuration["HOST"],
            port=configuration["PORT"]
        ),
        "workers": 1,
        "max_requests": worker_max_requests,
        "max_requests_jitter": worker_request_jitter,
    }

    app = create_app(settings_file)

    Server(app, options, configuration).run()


def get_arguments():
    parser = ArgumentParser(description="Text analysis service cli tool")

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("server", help="Start the tas server")
    run_parser.set_defaults(func=run)

    return parser.parse_args()


def main():
    args = get_arguments()

    args.func(args)
