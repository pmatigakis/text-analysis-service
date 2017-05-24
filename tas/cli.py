from os import getcwd, path, environ, execvp
from argparse import ArgumentParser
import hashlib

from consul import Consul, Check

from tas.configuration.loaders import Configuration


def _generate_service_id(service_name, host, port):
    """Create the service id for consul
    :param str service_name: the service name
    :param str host: the service address
    :param int port: the port on which the service listens to
    :rtype: str
    :return: the service id
    """
    service_info = "{}-{}-{}".format(service_name, host, port).encode("utf-8")

    return "{}".format(hashlib.md5(service_info).hexdigest())


def _register_service(configuration):
    client = Consul(
        host=configuration["CONSUL_HOST"],
        port=configuration["CONSUL_PORT"],
        scheme=configuration["CONSUL_SCHEME"],
        verify=configuration["CONSUL_VERIFY_SSL"]
    )

    health_address = "http://{host}:{port}/service/health"

    health_http = Check.http(
        url=health_address.format(
            host=configuration["HOST"],
            port=configuration["PORT"]
        ),
        interval=configuration["CONSUL_HEALTH_INTERVAL"],
        timeout=configuration["CONSUL_HEALTH_TIMEOUT"]
    )

    client.agent.service.register(
        name=configuration["SERVICE_NAME"],
        service_id=_generate_service_id(
            configuration["SERVICE_NAME"],
            configuration["HOST"],
            configuration["PORT"]
        ),
        address=configuration["HOST"],
        port=configuration["PORT"],
        check=health_http
    )


def _init_uwsgi_environment_variables(configuration):
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


def run(args):
    settings_file = path.join(getcwd(), "settings.py")

    configuration = Configuration.load_from_py(settings_file)

    if configuration.get("CONSUL_HOST") is not None:
        _register_service(configuration)

    _init_uwsgi_environment_variables(configuration)

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
