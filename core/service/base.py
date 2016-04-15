# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import os
import sys
import logging
import signal
import uuid
import random
from collections import defaultdict
import argparse
## Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.web
import tornado.netutil
import tornado.httpserver
import tornado.httpclient
from concurrent.futures import ThreadPoolExecutor
import setproctitle
import nsq
import ujson
## NOC modules
from noc.lib.debug import excepthook, error_report
from .config import Config
from .api import APIRequestHandler
from .doc import DocRequestHandler
from .mon import MonRequestHandler
from .sdl import SDLRequestHandler
from .rpc import RPCProxy


class Service(object):
    """
    Basic service implementation.

    * on_change_<var> - subscribed to changes of config variable <var>
    """
    # Service name
    name = None
    # Format string to set process name
    # config variables can be expanded as %(name)s
    process_name = "noc-%(name).10s"
    # Leader group name
    # Only one service in leader group can be running at a time
    # Config variables can be expanded as %(varname)s
    leader_group_name = None
    # Pooled service are used to distribute load between services.
    # Pool name set in NOC_POOL parameter or --pool option.
    # May be used in conjunction with leader_group_name
    # to allow only one instance of services per node or datacenter
    pooled = False

    ## List of API instances
    api = []
    ## Initialize gettext and process *language* configuration
    use_translation = False

    LOG_FORMAT = "%(asctime)s [%(name)s] %(message)s"

    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }

    def __init__(self):
        sys.excepthook = excepthook
        # Monkeypatch error reporting
        tornado.ioloop.IOLoop.handle_callback_exception = self.handle_callback_exception
        self.ioloop = None
        self.logger = None
        self.config = None
        self.service_id = str(uuid.uuid4())
        self.perf_metrics = defaultdict(int)
        self.executors = {}
        self.start_time = time.time()
        self.pid = os.getpid()
        self.nsq_readers = {}  # handler -> Reader
        self.nsq_writer = None

    def create_parser(self):
        """
        Return argument parser
        """
        return argparse.ArgumentParser()

    def add_arguments(self, parser):
        """
        Apply additional parser arguments
        """
        parser.add_argument(
            "--env",
            action="store",
            dest="env",
            default=os.environ.get("NOC_ENV", ""),
            help="NOC environment name"
        )
        parser.add_argument(
            "--dc",
            action="store",
            dest="dc",
            default=os.environ.get("NOC_DC", ""),
            help="NOC datacenter name"
        )
        parser.add_argument(
            "--node",
            action="store",
            dest="node",
            default=os.environ.get("NOC_NODE", ""),
            help="NOC node name"
        )
        parser.add_argument(
            "--loglevel",
            action="store",
            choices=list(self.LOG_LEVELS),
            dest="loglevel",
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            help="Logging level"
        )
        parser.add_argument(
            "--instance",
            action="store",
            dest="instance",
            type=int,
            default=0,
            help="Instance number"
        )
        parser.add_argument(
            "--numprocs",
            action="store",
            dest="numprocs",
            type=int,
            default=os.environ.get("NOC_NUMPROCS", "1"),
            help="Total instances"
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            default=False,
            help="Dump additional debugging info"
        )
        parser.add_argument(
            "--config",
            action="store",
            dest="config",
            default=os.environ.get("NOC_CONFIG", "etc/noc.yml"),
            help="Configuration path"
        )
        if self.pooled:
            parser.add_argument(
                "--pool",
                action="store",
                dest="pool",
                default=os.environ.get("NOC_POOL", ""),
                help="NOC pool name"
            )

    def handle_callback_exception(self, callback):
        sys.stdout.write("Exception in callback %r\n" % callback)
        error_report()

    @classmethod
    def die(cls, msg):
        """
        Dump message to stdout and terminate process with error code
        """
        sys.stdout.write(str(msg) + "\n")
        sys.stdout.flush()
        sys.exit(1)

    def setup_logging(self, loglevel=None):
        """
        Create new or setup existing logger
        """
        if not loglevel:
            loglevel = self.config.loglevel
        logger = logging.getLogger()
        if len(logger.handlers):
            # Logger is already initialized
            fmt = logging.Formatter(self.LOG_FORMAT, None)
            for h in logging.root.handlers:
                if isinstance(h, logging.StreamHandler):
                    h.stream = sys.stdout
                h.setFormatter(fmt)
            logging.root.setLevel(self.LOG_LEVELS[loglevel])
        else:
            # Initialize logger
            logging.basicConfig(
                stream=sys.stdout,
                format=self.LOG_FORMAT,
                level=self.LOG_LEVELS[loglevel]
            )
        self.logger = logging.getLogger(self.name)
        logging.captureWarnings(True)

    def setup_translation(self):
        from noc.core.translation import set_translation

        set_translation(self.name, self.config.language)

    def on_change_loglevel(self, old_value, new_value):
        if new_value not in self.LOG_LEVELS:
            self.logger.error("Invalid loglevel '%s'. Ignoring", new_value)
            return
        self.logger.warn("Changing loglevel to %s", new_value)
        logging.getLogger().setLevel(self.LOG_LEVELS[new_value])

    def log_separator(self, symbol="*", length=72):
        """
        Log a separator string to visually split log
        """
        self.logger.warn(symbol * length)

    def setup_signal_handlers(self):
        """
        Set up signal handlers
        """
        signal.signal(signal.SIGTERM, self.on_SIGTERM)
        signal.signal(signal.SIGHUP, self.on_SIGHUP)

    def set_proc_title(self):
        """
        Set process title
        """
        vars = {
            "name": self.name,
            "instance": self.config.instance or "",
            "pool": self.config.pool or ""
        }
        vars.update(self.config._conf)
        title = self.process_name % vars
        self.logger.debug("Setting process title to: %s", title)
        setproctitle.setproctitle(title)

    def start(self):
        """
        Run main server loop
        """
        parser = self.create_parser()
        self.add_arguments(parser)
        options = parser.parse_args(sys.argv[1:])
        cmd_options = vars(options)
        args = cmd_options.pop("args", ())
        # Bootstrap logging with --loglevel
        self.setup_logging(cmd_options["loglevel"])
        self.log_separator()
        # Read
        self.config = Config(self, **cmd_options)
        self.load_config()
        # Setup title
        self.set_proc_title()
        # Setup manhole
        if os.environ.get("NOC_MANHOLE"):
            import manhole
            manhole.install()
        # Setup signal handlers
        self.setup_signal_handlers()
        # Starting IOLoop
        if self.pooled:
            self.logger.warn(
                "Running service %s (pool: %s)",
                self.name, self.config.pool
            )
        else:
            self.logger.warn(
                "Running service %s", self.name
            )
        try:
            self.ioloop = tornado.ioloop.IOLoop.current()
            self.logger.warn("Activating service")
            self.activate()
            self.logger.warn("Starting IOLoop")
            self.ioloop.start()
        except KeyboardInterrupt:
            self.logger.warn("Interrupted by Ctrl+C")
        except Exception:
            error_report()
        finally:
            self.deactivate()
        self.logger.warn("Service %s has been terminated", self.name)

    def load_config(self):
        """
        Reload config
        """
        self.config.load(self.config.config)
        self.setup_logging()
        if self.use_translation:
            self.setup_translation()

    def stop(self):
        self.logger.warn("Stopping")
        self.ioloop.add_callback(self.deactivate)

    def on_SIGHUP(self, signo, frame):
        self.logger.warn("SIGHUP caught, rereading config")
        self.ioloop.add_callback(self.load_config)

    def on_SIGTERM(self, signo, frame):
        self.logger.warn("SIGTERM caught, Stopping")
        self.stop()

    def get_service_address(self):
        """
        Returns an (address, port) for HTTP service listener
        """
        addr, port = self.config.listen.split(":")
        port = int(port) + self.config.instance
        return addr, port

    def get_handlers(self):
        """
        Returns a list of additional handlers
        """
        return []

    def get_app_settings(self):
        """
        Returns tornado application settings
        """
        return {
            "template_path": os.getcwd(),
            "cookie_secret": "12345"
        }

    def activate(self):
        """
        Initialize services before run
        """
        handlers = [
            (r"^/mon/$", MonRequestHandler, {"service": self})
        ]
        if self.api:
            addr, port = self.get_service_address()
            sdl = {}  # api -> [methods]
            # Collect and register exposed API
            for a in self.api:
                url = "^/api/%s/$" % a.name
                self.logger.info(
                    "Supported API: %s at http://%s:%s/api/%s/",
                    a.name, addr, port, a.name
                )
                handlers += [(
                    url,
                    APIRequestHandler,
                    {"service": self, "api_class": a}
                )]
                # Populate sdl
                sdl[a.name] = a.get_methods()
            handlers += [
                ("^/doc/$", DocRequestHandler, {"service": self}),
                ("^/sdl.js", SDLRequestHandler, {"sdl": sdl})
            ]
        handlers += self.get_handlers()
        if handlers:
            addr, port = self.get_service_address()
            self.logger.info("Running HTTP APIs at http://%s:%s/",
                             addr, port)
            app = tornado.web.Application(handlers, **self.get_app_settings())
            http_server = tornado.httpserver.HTTPServer(app)
            http_server.listen(port, addr)
        self.ioloop.add_callback(self.on_activate)

    @tornado.gen.coroutine
    def deactivate(self):
        # Finally stop ioloop
        self.logger.info("Stopping IOLoop")
        self.ioloop.stop()

    def on_activate(self):
        """
        Called when service activated
        """
        pass

    def open_rpc(self, name, pool=None):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc)

    def get_mon_data(self):
        """
        Returns monitoring data
        """
        r = {
            "status": True,
            "service": self.name,
            "instance": self.config.instance,
            "node": self.config.node,
            "dc": self.config.dc,
            "config": self.config._conf,
            "pid": self.pid,
            # Current process uptime
            "uptime": time.time() - self.start_time
        }
        if self.executors:
            r["threadpools"] = {}
            for x in self.executors:
                r["threadpools"][x] = {
                    "qsize": self.executors[x]._work_queue.qsize(),
                    "threads": len(self.executors[x]._threads)
                }
        r.update(self.perf_metrics)
        return r

    def resolve_service(self, service, n=None):
        """
        Resolve service
        Returns n randomly selected choices
        @todo: Datacenter affinity
        """
        n = n or self.config.rpc_choose_services
        candidates = self.config.get_service(service)
        if not candidates:
            return []
        else:
            return random.sample(candidates, min(n, len(candidates)))

    def iter_rpc_retry_timeout(self):
        """
        Yield timeout to wait after unsuccessful RPC connection
        """
        for t in self.config.rpc_retry_timeout.split(","):
            yield float(t)

    def subscribe(self, topic, channel, handler):
        """
        Subscribe message to channel
        """
        def call_handler(message):
            try:
                data = ujson.loads(message.body)
            except ValueError as e:
                self.logger.debug("Cannot decode JSON message: %s", e)
                return True  # Broken message
            if isinstance(data, dict):
                return handler(message, **data)
            else:
                return handler(message, data)

        self.logger.debug("Subscribing to %s/%s", topic, channel)
        self.nsq_readers[handler] = nsq.Reader(
            message_handler=call_handler,
            topic=topic,
            channel=channel,
            lookupd_http_addresses=self.config.get_service("nsqlookupd")
        )

    def get_nsq_writer(self):
        if not self.nsq_writer:
            self.nsq_writer = nsq.Writer(["127.0.0.1:4150"])
        return self.nsq_writer

    def pub(self, topic, data):
        """
        Publish message to topic
        """
        w = self.get_nsq_writer()
        w.pub(topic, ujson.dumps(data))

    def mpub(self, topic, messages):
        """
        Publish multiple messages to topic
        """
        w = self.get_nsq_writer()
        w.mpub(topic, [ujson.dumps(m) for m in messages])

    def get_executor(self, name):
        """
        Return or start named executor
        """
        executor = self.executors.get(name)
        if not executor:
            xt = "%s_threads" % name
            executor = ThreadPoolExecutor(self.config[xt])
            self.executors[name] = executor
        return executor
