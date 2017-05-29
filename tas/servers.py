import logging
import hashlib

from gunicorn.app.base import BaseApplication
from consul import Consul, Check


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


class Server(BaseApplication):
    """The text analysis service server

    Server is responsible for registering tas to consul and starting the
    application server
    """

    def __init__(self, app, options=None, configuration=None):
        """Create a new server object

        :param falcon.API app: the falcon application
        :param dict options: the gunicorn configuration options
        :param dict configuration: the wsgi application configuration
        """
        self.options = options or {}
        self.configuration = configuration or {}
        self.application = app
        super(Server, self).__init__()

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

    def _on_starting(self, server):
        """Server is initializing

        :param server: the server object
        """
        logger.info("server started")

        if self.configuration["CONSUL_HOST"] is not None:
            self._register_service()

    def load_config(self):
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key, value)

        # we have to setup the hooks using lambdas in order to avoid the
        # function arity checks of gunicorn
        self.cfg.set("on_starting", lambda server: self._on_starting(server))

    def load(self):
        return self.application
