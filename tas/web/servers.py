import logging
import hashlib
from os import getcwd, path

from gunicorn.app.base import BaseApplication
from consul import Consul, Check

from tas.configuration.loaders import Configuration
from tas.web.application import create_app


logger = logging.getLogger(__name__)


def generate_service_id(service_name, host, port):
    """Create the service id for consul

    :param str service_name: the service name
    :param str host: the service address
    :param int port: the port on which the service listens to
    :rtype: str
    :return: the service id
    """
    service_info = "{}-{}-{}".format(service_name, host, port).encode("utf-8")

    return "{}".format(hashlib.md5(service_info).hexdigest())


def _extract_gunicorn_options(configuration):
    options = {
        "preload_app": False,
        "bind": "{host}:{port}".format(
            host=configuration["HOST"],
            port=configuration["PORT"]
        ),
        "workers": configuration["WORKERS"],
        "worker_class": "sync",
        "max_requests": configuration["WORKER_MAX_REQUESTS"],
        "max_requests_jitter":
            configuration["WORKER_MAX_REQUESTS_JITTER"],
    }

    return options


class Server(BaseApplication):
    """A standalone gunicorn server"""

    def __init__(self, app, options=None):
        """Create a new Server object

        :param falcon.API app: the falcon application
        :param dict options: the gunicorn configuration
        """
        self.options = options or {}
        self.application = app

        super(Server, self).__init__()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key, value)

    def load(self):
        return self.application


class TextAnalysisServiceServer(Server):
    """The text analysis service server

    TextAnalysisServiceServer is responsible for registering tas to consul and
    starting the application server
    """

    def __init__(self, configuration_path):
        """Create a new TextAnalysisServiceServer object

        :param str configuration_path: the path to the application
            configuration file
        """
        settings_file = path.join(getcwd(), "settings.py")
        self.configuration = Configuration.load_from_py(settings_file)

        options = _extract_gunicorn_options(self.configuration)
        app = create_app(settings_file)

        super(TextAnalysisServiceServer, self).__init__(app, options)

    def _register_service(self):
        logger.info("registering service to consul")

        client = Consul(
            host=self.configuration["CONSUL_HOST"],
            port=self.configuration["CONSUL_PORT"],
            scheme=self.configuration["CONSUL_SCHEME"],
            verify=self.configuration["CONSUL_VERIFY_SSL"]
        )

        health_address = "http://{host}:{port}/service/health"

        health_http = Check.http(
            url=health_address.format(
                host=self.configuration["HOST"],
                port=self.configuration["PORT"]
            ),
            interval=self.configuration["CONSUL_HEALTH_INTERVAL"],
            timeout=self.configuration["CONSUL_HEALTH_TIMEOUT"]
        )

        client.agent.service.register(
            name=self.configuration["SERVICE_NAME"],
            service_id=generate_service_id(
                self.configuration["SERVICE_NAME"],
                self.configuration["HOST"],
                self.configuration["PORT"]
            ),
            address=self.configuration["HOST"],
            port=self.configuration["PORT"],
            check=health_http
        )

    def _deregister_service(self):
        """Deregister the service"""
        logger.info("deregistering service from consul")

        client = Consul(
            host=self.configuration["CONSUL_HOST"],
            port=self.configuration["CONSUL_PORT"],
            scheme=self.configuration["CONSUL_SCHEME"],
            verify=self.configuration["CONSUL_VERIFY_SSL"]
        )

        service_id = generate_service_id(
            self.configuration["SERVICE_NAME"],
            self.configuration["HOST"],
            self.configuration["PORT"]
        )

        client.agent.service.deregister(
            service_id=service_id
        )

    def _on_starting(self, server):
        """Server is initializing

        :param server: the server object
        """
        logger.info("server started")

        if self.configuration["CONSUL_HOST"] is not None:
            self._register_service()

    def _on_exit(self, server):
        """Server is shutting down

        :param server: the server object
        """
        logger.info("server stopped")

        if self.configuration["CONSUL_HOST"] is not None:
            self._deregister_service()

    def load_config(self):
        super(TextAnalysisServiceServer, self).load_config()

        # we have to setup the hooks using lambdas in order to avoid the
        # function arity checks of gunicorn
        self.cfg.set("on_starting", lambda server: self._on_starting(server))
        self.cfg.set("on_exit", lambda server: self._on_exit(server))
