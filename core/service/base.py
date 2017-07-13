# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
import os
import sys
import logging
import signal
import uuid
import argparse
import functools
import socket
from collections import defaultdict
# Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.web
import tornado.netutil
import tornado.httpserver
import setproctitle
import nsq
import ujson
import threading
# NOC modules
from noc.config import config
from noc.core.debug import excepthook, error_report
from .api import APIRequestHandler
from .doc import DocRequestHandler
from .mon import MonRequestHandler
from .metrics import MetricsHandler
from .health import HealthRequestHandler
from .sdl import SDLRequestHandler
from .rpc import RPCProxy
from .ctl import CtlAPI
from .loader import set_service
from noc.core.perf import metrics, apply_metrics
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from noc.core.threadpool import ThreadPoolExecutor
from noc.core.nsq.reader import Reader as NSQReader
from noc.config import config


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
    # Leader lock name
    # Only one active instace per leader lock can be active
    # at given moment
    # Config variables can be expanded as %(varname)s
    leader_lock_name = None

    # Leader group name
    # Only one service in leader group can be running at a time
    # Config variables can be expanded as %(varname)s
    # @todo: Deprecated, must be removed
    leader_group_name = None
    # Pooled service are used to distribute load between services.
    # Pool name set in NOC_POOL parameter or --pool option.
    # May be used in conjunction with leader_group_name
    # to allow only one instance of services per node or datacenter
    pooled = False

    # Run NSQ writer on service startup
    require_nsq_writer = False
    # List of API instances
    api = []
    # Request handler class
    api_request_handler = APIRequestHandler
    # Initialize gettext and process *language* configuration
    use_translation = False
    # Initialize jinja2 templating engine
    use_jinja = False
    # Register traefik backend if not None
    traefik_backend = None
    # Traefik frontend rule
    # i.e. PathPrefix:/api/<name>
    traefik_frontend_rule = None

    LOG_FORMAT = config.log_format

    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }

    NSQ_PUB_RETRY_DELAY = config.nsqd.nsq_pub_retry_delay
    CH_CHUNK_SIZE = config.nsqd.ch_chunk_size

    class RegistrationError(Exception):
        pass

    def __init__(self):
        set_service(self)
        sys.excepthook = excepthook
        # Monkeypatch error reporting
        tornado.ioloop.IOLoop.handle_callback_exception = self.handle_callback_exception
        self.ioloop = None
        self.logger = None
        self.service_id = str(uuid.uuid4())
        self.perf_metrics = metrics
        self.executors = {}
        self.start_time = time.time()
        self.pid = os.getpid()
        self.nsq_readers = {}  # handler -> Reader
        self.nsq_writer = None
        self._metrics = []
        self._ch_metrics = defaultdict(list)
        self.metrics_lock = threading.Lock()
        self.metrics_callback = None
        self.ch_metrics_callback = None
        self.dcs = None
        # Effective address and port
        self.server = None
        self.address = None
        self.port = None
        self.is_active = False
        self.close_callbacks = []
        # Can be initialized in subclasses
        self.scheduler = None

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
            default=config.node,
            help="NOC node name"
        )
        parser.add_argument(
            "--loglevel",
            action="store",
            choices=list(self.LOG_LEVELS),
            dest="loglevel",
            default=config.loglevel,
            help="Logging level"
        )
        parser.add_argument(
            "--instance",
            action="store",
            dest="instance",
            type=int,
            default=config.instance,
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
            "--dcs",
            action="store",
            dest="dcs",
            default=DEFAULT_DCS,
            help="Distributed Coordinated Storage URL"
        )
        if self.pooled:
            parser.add_argument(
                "--pool",
                action="store",
                dest="pool",
                default=config.pool,
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
            loglevel = config.loglevel
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
        from noc.core.translation import set_translation, ugettext

        set_translation(self.name, config.language)
        if self.use_jinja:
            from jinja2.defaults import DEFAULT_NAMESPACE
            if "_" not in DEFAULT_NAMESPACE:
                DEFAULT_NAMESPACE["_"] = ugettext

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
        v = {
            "name": self.name,
            "instance": config.instance or "",
            "pool": config.pool or ""
        }
        title = self.process_name % v
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
        # Setup title
        self.set_proc_title()
        # Setup signal handlers
        self.setup_signal_handlers()
        # Starting IOLoop
        self.is_active = True
        if self.pooled:
            self.logger.warn(
                "Running service %s (pool: %s)",
                self.name, config.pool
            )
        else:
            self.logger.warn(
                "Running service %s", self.name
            )
        try:
            if config.features.use_uvlib:
                from tornaduv import UVLoop
                self.logger.warn("Using libuv")
                tornado.ioloop.IOLoop.configure(UVLoop)
            self.ioloop = tornado.ioloop.IOLoop.instance()
            # Initialize DCS
            self.dcs = get_dcs(cmd_options["dcs"], self.ioloop)
            # Activate service
            self.ioloop.add_callback(self.activate)
            self.logger.warn("Starting IOLoop")
            self.ioloop.start()
        except KeyboardInterrupt:
            self.logger.warn("Interrupted by Ctrl+C")
        except self.RegistrationError:
            self.logger.info("Registration failed")
        except Exception:
            error_report()
        finally:
            if self.ioloop:
                self.ioloop.add_callback(self.deactivate())
        for cb, args, kwargs in self.close_callbacks:
            cb(*args, **kwargs)
        self.logger.warn("Service %s has been terminated", self.name)

    def load_config(self):
        """
        Reload config
        """
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
        if self.address and self.port:
            return self.address, self.port
        if config.listen:
            addr, port = config.listen.split(":")
            port_tracker = config.instance
        else:
            addr, port = "auto", 0
            port_tracker = 0
        if addr == "auto":
            addr = os.environ.get("HOSTNAME", socket.gethostname())
            self.logger.info("Autodetecting address: auto -> %s", addr)
        addr = socket.gethostbyname(addr)
        port = int(port) + port_tracker
        return addr, port

    def update_service_address(self):
        """
        Update service address and port from tornado TCPServer
        :param server:
        :return:
        """
        for f in self.server._sockets:
            sock = self.server._sockets[f]
            self.address, self.port = sock.getsockname()
            break

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
            "cookie_secret": config.secret_key,
            "log_function": self.log_request
        }

    def activate(self):
        """
        Initialize services before run
        """
        self.logger.warn("Activating service")
        handlers = [
            (r"^/mon/$", MonRequestHandler, {"service": self}),
            (r"^/metrics$", MetricsHandler, {"service": self}),
            (r"^/health/$", HealthRequestHandler, {"service": self})
        ]
        api = [CtlAPI]
        if self.api:
            api += self.api
        addr, port = self.get_service_address()
        sdl = {}  # api -> [methods]
        # Collect and register exposed API
        for a in api:
            url = "^/api/%s/$" % a.name
            handlers += [(
                url,
                self.api_request_handler,
                {"service": self, "api_class": a}
            )]
            # Populate sdl
            sdl[a.name] = a.get_methods()
        if self.api:
            handlers += [
                ("^/api/%s/doc/$" % self.name, DocRequestHandler, {"service": self}),
                ("^/api/%s/sdl.js" % self.name, SDLRequestHandler, {"sdl": sdl})
            ]
        handlers += self.get_handlers()
        app = tornado.web.Application(handlers, **self.get_app_settings())
        self.server = tornado.httpserver.HTTPServer(
            app,
            xheaders=True,
            no_keep_alive=True
        )
        self.server.listen(port, addr)
        # Get effective address and port
        self.update_service_address()
        #
        self.logger.info("Running HTTP APIs at http://%s:%s/",
                         self.address, self.port)
        for a in api:
            self.logger.info(
                "Supported API: %s at http://%s:%s/api/%s/",
                a.name, self.address, self.port, a.name
            )
        #
        if self.require_nsq_writer:
            self.get_nsq_writer()
        self.ioloop.add_callback(self.on_register)

    @tornado.gen.coroutine
    def deactivate(self):
        if not self.is_active:
            raise tornado.gen.Return()
        self.is_active = False
        self.logger.info("Deactivating")
        # Shutdown API
        self.logger.info("Stopping API")
        self.server.stop()
        # Release registration
        if self.dcs:
            self.logger.info("Deregistration")
            yield self.dcs.deregister()
        # Shutdown schedulers
        if self.scheduler:
            try:
                self.logger.info("Shutting down scheduler")
                yield self.scheduler.shutdown()
            except tornado.gen.TimeoutError:
                self.logger.info(
                    "Timed out when shutting down scheduler")
        # Shutdown executors
        if self.executors:
            self.logger.info("Shutting down executors")
            for x in self.executors:
                try:
                    self.logger.info("Shutting down %s", x)
                    yield self.executors[x].shutdown()
                except tornado.gen.TimeoutError:
                    self.logger.info(
                        "Timed out when shutting down %s", x
                    )
        # Custom deactivation
        yield self.on_deactivate()
        # Finally stop ioloop
        self.dcs = None
        self.logger.info("Stopping IOLoop")
        self.ioloop.stop()
        m = {}
        apply_metrics(m)
        self.logger.info("Post-mortem metrics: %s", m)
        self.die()

    def get_register_tags(self):
        tags = []
        if self.traefik_backend and self.traefik_frontend_rule:
            tags += [
                "traefik.backend=%s" % self.traefik_backend,
                "traefik.frontend.rule=%s" % self.traefik_frontend_rule
            ]
            weight = self.get_backend_weight()
            if weight:
                tags += ["traefik.backend.weight=%s" % weight]
            limit = self.get_backend_limit()
            if limit:
                tags += ["traefik.backend.maxconn.amount=%s" % limit]
        return tags

    @tornado.gen.coroutine
    def on_register(self):
        addr, port = self.get_service_address()
        r = yield self.dcs.register(
            self.name, addr, port,
            pool=config.pool or None,
            lock=self.get_leader_lock_name(),
            tags=self.get_register_tags()
        )
        if r:
            # Finally call on_activate
            yield self.on_activate()
            self.logger.info("Service is active")
        else:
            raise self.RegistrationError()

    @tornado.gen.coroutine
    def on_activate(self):
        """
        Called when service activated
        """
        raise tornado.gen.Return()

    @tornado.gen.coroutine
    def acquire_slot(self):
        if self.pooled:
            name = "%s-%s" % (self.name, config.pool)
        else:
            name = self.name
        slot_number, total_slots = yield self.dcs.acquire_slot(
            name,
            config.global_n_instances
        )
        raise tornado.gen.Return((slot_number, total_slots))

    @tornado.gen.coroutine
    def on_deactivate(self):
        raise tornado.gen.Return()

    def open_rpc(self, name, pool=None, sync=False, hints=None):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc, sync=sync, hints=hints)

    def get_mon_status(self):
        return True

    def get_mon_data(self):
        """
        Returns monitoring data
        """
        r = {
            "status": self.get_mon_status(),
            "service": self.name,
            "instance": str(config.instance),
            "node": config.node,
            "pid": self.pid,
            # Current process uptime
            "uptime": time.time() - self.start_time
        }
        if self.pooled:
            r["pool"] = config.pool
        if self.executors:
            for x in self.executors:
                self.executors[x].apply_metrics(r)
        apply_metrics(r)
        return r

    def iter_rpc_retry_timeout(self):
        """
        Yield timeout to wait after unsuccessful RPC connection
        """
        for t in config.rpc.retry_timeout.split(","):
            yield float(t)

    def subscribe(self, topic, channel, handler, raw=False, **kwargs):
        """
        Subscribe message to channel
        """
        def call_json_handler(message):
            self.perf_metrics[metric_in] += 1
            try:
                data = ujson.loads(message.body)
            except ValueError as e:
                self.perf_metrics[metric_decode_fail] += 1
                self.logger.debug("Cannot decode JSON message: %s", e)
                return True  # Broken message
            if isinstance(data, dict):
                r = handler(message, **data)
            else:
                r = handler(message, data)
            if r:
                self.perf_metrics[metric_processed] += 1
            elif message.is_async():
                message.on("finish", on_finish)
            else:
                self.perf_metrics[metric_deferred] += 1
            return r

        def call_raw_handler(message):
            self.perf_metrics[metric_in] += 1
            r = handler(message, message.body)
            if r:
                self.perf_metrics[metric_processed] += 1
            elif message.is_async():
                message.on("finish", on_finish)
            else:
                self.perf_metrics[metric_deferred] += 1
            return r

        def on_finish(*args, **kwargs):
            self.perf_metrics[metric_processed] += 1

        t = topic.replace(".", "_")
        metric_in = "nsq_msg_in_%s" % t
        metric_decode_fail = "nsq_msg_decode_fail_%s" % t
        metric_processed = "nsq_msg_processed_%s" % t
        metric_deferred = "nsq_msg_deferred_%s" % t
        lookupd = [str(a) for a in config.nsqlookupd.addresses]
        self.logger.info("Subscribing to %s/%s (lookupd: %s)",
                         topic, channel, ", ".join(lookupd))
        self.nsq_readers[handler] = NSQReader(
            message_handler=call_raw_handler if raw else call_json_handler,
            topic=topic,
            channel=channel,
            lookupd_http_addresses=lookupd,
            **kwargs
        )

    def get_nsq_writer(self):
        if not self.nsq_writer:
            self.logger.info("Opening NSQ Writer")
            self.nsq_writer = nsq.Writer([config.nsqd.addresses])
        return self.nsq_writer

    def pub(self, topic, data):
        """
        Publish message to topic
        """
        def finish_pub(conn, data):
            if isinstance(data, nsq.Error):
                self.logger.info(
                    "Failed to pub to topic '%s'. Retry",
                    topic
                )
                w.io_loop.call_later(
                    self.NSQ_PUB_RETRY_DELAY,
                    functools.partial(
                        w.pub, topic, msg, callback=finish_pub
                    )
                )

        w = self.get_nsq_writer()
        msg = ujson.dumps(data)
        w.pub(topic, msg, callback=finish_pub)

    def mpub(self, topic, messages):
        """
        Publish multiple messages to topic
        """
        def finish_pub(conn, data):
            if isinstance(data, nsq.Error):
                self.logger.info(
                    "Failed to mpub to topic '%s': %s. Retry",
                    topic, data
                )
                w.io_loop.call_later(
                    self.NSQ_PUB_RETRY_DELAY,
                    functools.partial(
                        w.mpub, topic, msg, callback=finish_pub
                    )
                )

        w = self.get_nsq_writer()
        msg = [ujson.dumps(m) for m in messages]
        w.mpub(topic, msg, callback=finish_pub)

    def get_executor(self, name):
        """
        Return or start named executor
        """
        executor = self.executors.get(name)
        if not executor:
            xt = "%s.%s_threads" % (self.name, name)
            max_threads = config.get_parameter(xt)
            self.logger.info(
                "Starting threadpool executor %s (up to %d threads)",
                name, max_threads
            )
            executor = ThreadPoolExecutor(max_threads, name=name)
            self.executors[name] = executor
        return executor

    def register_metrics(self, metrics):
        """
        Register metrics to send
        :param metric: List of strings
        """
        if not isinstance(metrics, (set, list)):
            metrics = [metrics]
        with self.metrics_lock:
            if not self.metrics_callback:
                self.metrics_callback = tornado.ioloop.PeriodicCallback(
                    self.send_metrics, 100, self.ioloop
                )
                self.metrics_callback.start()
            self._metrics += [str(x) for x in metrics]

    def register_ch_metrics(self, fields, metrics):
        """
        Register metrics to send (Clickhouse version)
        :param fields: String containing "<table>.<field1>...<fieldN>"
        :param metrics: list of tab-separated strings with values
        :return:
        """
        with self.metrics_lock:
            if not self.ch_metrics_callback:
                self.ch_metrics_callback = tornado.ioloop.PeriodicCallback(
                    self.send_ch_metrics, 250, self.ioloop
                )
                self.ch_metrics_callback.start()
            self._ch_metrics[fields] += metrics

    @tornado.gen.coroutine
    def send_metrics(self):
        if not self._metrics:
            return
        w = self.get_nsq_writer()
        with self.metrics_lock:
            w.pub("metrics", "\n".join(self._metrics))
            self._metrics = []

    @tornado.gen.coroutine
    def send_ch_metrics(self):
        if not self._ch_metrics:
            return
        w = self.get_nsq_writer()
        with self.metrics_lock:
            data = self._ch_metrics
            self._ch_metrics = defaultdict(list)
        for fields in data:
            to_send = data[fields]
            while to_send:
                chunk, to_send = to_send[:self.CH_CHUNK_SIZE], to_send[self.CH_CHUNK_SIZE:]
                w.pub("chwriter", "%s\n%s\n" % (
                    fields, "\n".join(chunk)))

    def log_request(self, handler):
        """
        Custom HTTP Log request handler
        :param handler:
        :return:
        """
        status = handler.get_status()
        method = handler.request.method
        uri = handler.request.uri
        remote_ip = handler.request.remote_ip
        if status == 200 and uri == "/mon/" and method == "GET":
            self.logger.debug("Monitoring request (%s)", remote_ip)
            self.perf_metrics["mon_requests"] += 1
        elif status == 200 and uri.startswith("/health/") and method == "GET":
            pass
        else:
            self.logger.info(
                "%s %s (%s) %.2fms",
                method, uri, remote_ip,
                1000.0 * handler.request.request_time()
            )
            self.perf_metrics["http_requests"] += 1
            self.perf_metrics["http_requests_%s" % method.lower()] += 1
            self.perf_metrics["http_response_%s" % status] += 1

    def get_leader_lock_name(self):
        if self.leader_lock_name:
            return self.leader_lock_name % {"pool": config.pool}
        else:
            return None

    def add_close_callback(self, cb, *args, **kwargs):
        self.close_callbacks += [(cb, args, kwargs)]

    def get_backend_weight(self):
        """
        Return backend weight for weighted load balancers
        (i.e. traefik).
        Return None for default weight
        :return:
        """
        return None

    def get_backend_limit(self):
        """
        Return backend connection limit for load balancers
        (i.e. traefik)
        Return None for no limits
        :return:
        """
        return None

    def is_valid_health_check(self, service_id):
        """
        Check received service id matches own service id
        :param service_id:
        :return:
        """
        if (self.dcs and self.dcs.health_check_service_id and
                self.dcs.health_check_service_id != service_id):
            return False
        else:
            return True
