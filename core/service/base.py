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
import functools
## Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.web
import tornado.netutil
import tornado.httpserver
import tornado.httpclient
from concurrent.futures import ThreadPoolExecutor
import nsq
import ujson
import threading
## NOC modules
from noc.lib.debug import excepthook, error_report
from noc.config import config
from .api import APIRequestHandler
from .doc import DocRequestHandler
from .mon import MonRequestHandler
from .health import HealthRequestHandler
from .sdl import SDLRequestHandler
from .rpc import RPCProxy
from .ctl import CtlAPI
from noc.core.perf import metrics, apply_metrics

class Service(object):
    """
    Basic service implementation.
    """
    # Service name
    name = None
    # Leader group name
    # Only one service in leader group can be running at a time
    # Config variables can be expanded as %(varname)s
    leader_group_name = None
    # Pooled service are used to distribute load between services.
    # Pool name set in NOC_POOL parameter or --pool option.
    # May be used in conjunction with leader_group_name
    # to allow only one instance of services per node or datacenter
    pooled = False

    ## Run NSQ writer on service startup
    require_nsq_writer = False
    ## List of API instances
    api = []
    ## Request handler class
    api_request_handler = APIRequestHandler
    ## Initialize gettext and process *language* configuration
    use_translation = False
    ## Initialize jinja2 templating engine
    use_jinja = False

    NSQ_PUB_RETRY_DELAY = 0.1

    def __init__(self):
        sys.excepthook = excepthook
        # Monkeypatch error reporting
        tornado.ioloop.IOLoop.handle_callback_exception = self.handle_callback_exception
        self.ioloop = None
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.service_id = str(uuid.uuid4())
        self.perf_metrics = metrics
        self.executors = {}
        self.start_time = time.time()
        self.pid = os.getpid()
        self.nsq_readers = {}  # handler -> Reader
        self.nsq_writer = None
        self._metrics = []
        self.metrics_lock = threading.Lock()
        self.metrics_callback = None
        self.setup_translation()

    def create_parser(self):
        """
        Return argument parser
        """
        return argparse.ArgumentParser()

    def add_arguments(self, parser):
        """
        Apply additional parser arguments
        """
        pass

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

    def setup_translation(self):
        from noc.core.translation import set_translation, ugettext

        set_translation(self.name, self.config.language)
        if self.use_jinja:
            from jinja2.defaults import DEFAULT_NAMESPACE
            if "_" not in DEFAULT_NAMESPACE:
                DEFAULT_NAMESPACE["_"] = ugettext

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
        self.log_separator()
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
            if os.environ.get("NOC_LIBUV"):
                from tornaduv import UVLoop
                self.logger.warn("Using libuv")
                tornado.ioloop.IOLoop.configure(UVLoop)
            self.ioloop = tornado.ioloop.IOLoop.instance()
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

    def stop(self):
        self.logger.warn("Stopping")
        self.ioloop.add_callback(self.deactivate)

    def on_SIGHUP(self, signo, frame):
        self.logger.warn("SIGHUP caught, not rereading config")

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
            "cookie_secret": self.config.secret_key,
            "log_function": self.log_request
        }

    def activate(self):
        """
        Initialize services before run
        """
        handlers = [
            (r"^/mon/$", MonRequestHandler, {"service": self}),
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
            self.logger.info(
                "Supported API: %s at http://%s:%s/api/%s/",
                a.name, addr, port, a.name
            )
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
        addr, port = self.get_service_address()
        self.logger.info("Running HTTP APIs at http://%s:%s/",
                         addr, port)
        app = tornado.web.Application(handlers, **self.get_app_settings())
        http_server = tornado.httpserver.HTTPServer(
            app,
            xheaders=True
        )
        http_server.listen(port, addr)
        if self.require_nsq_writer:
            self.get_nsq_writer()
        self.ioloop.add_callback(self.on_activate)

    @tornado.gen.coroutine
    def deactivate(self):
        self.logger.info("Deactivating")
        yield self.on_deactivate()
        # Finally stop ioloop
        self.logger.info("Stopping IOLoop")
        self.ioloop.stop()

    @tornado.gen.coroutine
    def on_activate(self):
        """
        Called when service activated
        """
        raise tornado.gen.Return()

    @tornado.gen.coroutine
    def on_deactivate(self):
        raise tornado.gen.Return()

    def open_rpc(self, name, pool=None):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc)

    def get_mon_status(self):
        return True

    def get_mon_data(self):
        """
        Returns monitoring data
        """
        import os
        r = {
            "status": self.get_mon_status(),
            "service": self.name,
            "instance": str(self.config.instance),
            "node": os.environ.get("HOSTNAME"),
            "pid": self.pid,
            # Current process uptime
            "uptime": time.time() - self.start_time
        }
        if self.pooled:
            r["pool"] = self.config.pool
        if self.executors:
            for x in self.executors:
                r["threadpool_%s_qsize" % x] = self.executors[x]._work_queue.qsize()
                r["threadpool_%s_threads" % x] = len(self.executors[x]._threads)
        r = apply_metrics(r)
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
        for t in self.config.rpc.retry_timeout.split(","):
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
        lookupd = self.config.nsqlookupd.hosts
        self.logger.info("Subscribing to %s/%s (lookupd: %s)",
                         topic, channel, lookupd)
        self.nsq_readers[handler] = nsq.Reader(
            message_handler=call_raw_handler if raw else call_json_handler,
            topic=topic,
            channel=channel,
            lookupd_http_addresses=lookupd,
            **kwargs
        )

    def get_nsq_writer(self):
        if not self.nsq_writer:
            self.logger.info("Opening NSQ Writer")
            self.nsq_writer = nsq.Writer(config.nsqd.hosts)
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
            xt = "%s_threads" % name
            executor = ThreadPoolExecutor(self.config.sae.db_threads)
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

    @tornado.gen.coroutine
    def send_metrics(self):
        if not self._metrics:
            return
        w = self.get_nsq_writer()
        with self.metrics_lock:
            w.pub("metrics", "\n".join(self._metrics))
            self._metrics = []

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
        else:
            self.logger.info(
                "%s %s (%s) %.2fms",
                method, uri, remote_ip,
                1000.0 * handler.request.request_time()
            )
            self.perf_metrics["http_requests"] += 1
            self.perf_metrics["http_requests_%s" % method.lower()] += 1
            self.perf_metrics["http_response_%s" % status] += 1
