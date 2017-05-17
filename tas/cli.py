from os import getcwd, path, environ, execvp
from argparse import ArgumentParser

from tas.configuration.loaders import Configuration


def run(args):
    settings_file = path.join(getcwd(), "settings.py")

    configuration = Configuration.load_from_py(settings_file)

    uwsgi_settings = {
        "UWSGI_MODULE": "tas.wsgi",
        "UWSGI_CALLABLE": "wsgi_app()",
        "UWSGI_MASTER": "1",
        "UWSGI_PROCESSES": "1",
        "UWSGI_DIE_ON_TERM": "1",
        "UWSGI_LAZY_APPS": "1",
        "UWSGI_VHOST": "1"
    }

    uwsgi_settings.update(configuration.get("UWSGI", {}))

    host = configuration.get("HOST", "127.0.0.1")
    port = configuration.get("PORT", 5000)

    uwsgi_settings["UWSGI_HTTP"] = "{host}:{port}".format(host=host, port=port)

    for configuration_variable, value in uwsgi_settings.items():
        environ[configuration_variable] = str(value)

    execvp("uwsgi", ("uwsgi",))


def get_arguments():
    parser = ArgumentParser(description="Text analysis service cli tool")

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("server", help="Start the tas server")
    run_parser.set_defaults(func=run)

    return parser.parse_args()


def main():
    args = get_arguments()

    args.func(args)
