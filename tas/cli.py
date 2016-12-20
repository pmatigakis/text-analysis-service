from os import getcwd, path
from wsgiref import simple_server
from argparse import ArgumentParser

from tas.application import create_app, load_settings


def run(args):
    settings_file = path.join(getcwd(), "settings.ini")

    app = create_app(settings_file)

    settings = load_settings(settings_file)

    host = args.host or settings.get("debug-server]", "host")
    port = args.port or settings.getint("debug-server]", "port")

    httpd = simple_server.make_server(host, port, app)
    httpd.serve_forever()


def get_arguments():
    parser = ArgumentParser(description="Text analysis service cli tool")

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser(
        "run", help="Start the development server")

    run_parser.add_argument(
        "--host", default="127.0.0.1", help="The server's host address")

    run_parser.add_argument(
        "--port", default=8000, type=int, help="The server's port")

    run_parser.set_defaults(func=run)

    return parser.parse_args()


def main():
    args = get_arguments()

    args.func(args)
