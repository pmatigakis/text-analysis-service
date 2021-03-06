from distutils.util import strtobool
import os
import re

from dotenv import load_dotenv

load_dotenv()

# run the classifier in debug model
DEBUG = bool(strtobool(os.getenv("DEBUG", "False")))

# run the classifier in testing model. Not doing something special at the moment
# so you can ignore this setting
TESTING = bool(strtobool(os.getenv("TESTING", "False")))

KEYWORD_STOP_LIST = "SmartStoplist.txt"

# set the address that the server will listen to. With a bit of ugly hacking
# we will get the address to use when the server runs inside a docker container
host = os.getenv("HOST")
if host is None:
    host_pattern = re.compile(r"^(.+?)\s+{}$".format(os.getenv("HOSTNAME")))

    with open("/etc/hosts", "r") as f:
        for line in f:
            m = host_pattern.match(line)
            if m:
                host = m.group(1)
                break

    if host is None:
        raise RuntimeError("failed to find the container ip address")

HOST = host

# set the port where the server will listen to
PORT = int(os.getenv("PORT", 8020))

# the number of request a worker will serve before it is restarted
WORKER_MAX_REQUESTS = int(os.getenv("WORKER_MAX_REQUESTS", 500))

# set the worker request jitte
WORKER_MAX_REQUESTS_JITTER = int(os.getenv("WORKER_MAX_REQUESTS_JITTER", 30))

# set the number of workers to start
WORKERS = int(os.getenv("WORKERS", 4))

# send statistics to this statsd server
STATSD_HOST = os.getenv("STATSD_HOST")
STATSD_PORT = int(os.getenv("STATSD_PORT", 8125))

# the settings for the consul health checks
CONSUL_HOST = os.getenv("CONSUL_HOST")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
CONSUL_SCHEME = os.getenv("CONSUL_SCHEME", "http")
CONSUL_VERIFY_SSL = bool(strtobool(os.getenv("CONSUL_VERIFY_SSL", "True")))
CONSUL_HEALTH_INTERVAL = "10s"
CONSUL_HEALTH_TIMEOUT = "5s"

__handlers = {
    'console': {
        'level': os.getenv("CONSOLE_LOG_LEVEL", "INFO"),
        'class': 'logging.StreamHandler',
        'formatter': 'verbose'
    }
}

# set the sentry dsn to use for exception logging
__sentry_dsn = os.getenv("SENTRY_DSN")
if __sentry_dsn:
    __handlers["sentry"] = {
        'level': os.getenv("SENTRY_LOG_LEVEL", "ERROR"),
        'class': 'raven.handlers.logging.SentryHandler',
        'dsn': __sentry_dsn
    }

# configure the loggers
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "%(asctime)s %(levelname)s [%(process)d:%(thread)d] %(name)s [%(pathname)s:%(funcName)s:%(lineno)d] %(message)s"
        }
    },
    'handlers': __handlers,
    'loggers': {
        'tas': {
            'handlers': __handlers.keys(),
            'propagate': True
        },
        'metricslib': {
            'handlers': __handlers.keys(),
            'propagate': True
        }
    },
    "root": {
        'level': 'INFO',
    }
}
