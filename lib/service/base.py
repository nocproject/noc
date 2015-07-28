# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import sys
import logging
from optparse import (make_option, OptionParser,
                      OptionError, OptParseError)
import signal
import uuid
import socket
import json
## Third-party modules
from tornado import ioloop
import tornado.gen
import tornado.web
import tornado.netutil
import tornado.httpserver
import consul.tornado
import consul.base
import consul
import nsq
## NOC modules
from .config import Config
from noc.sa.interfaces.base import DictParameter, StringParameter
from .api.base import ServiceAPI, ServiceSubscriber
from .api.mon import MonAPI
from .doc import DocRequestHandler
from .rpc import RPCProxy


class Service(object):
    """
    Basic service implementation.

    * on_change_<var> - subscribed to changes of config variable <var>
    """
    # Service name
    name = None
    # Leager group name
    # Only one service in leader group can be running at a time
    # Config variables can be expanded as %(varname)s
    leader_group_name = None
    # Pooled service are used to distribute load between services.
    # Pool name set in NOC_POOL parameter or --pool option.
    # May be used in conjunction with leader_group_name
    # to allow only one instance of services per node or datacenter
    # Service became pooled whenever any of advertised APIs
    # declared at AL_POOL level
    _pooled = None
    #
    usage = "usage: %prog [options] arg1 arg2 ..."
    # CLI option list
    option_list = [
        make_option(
            "--loglevel",
            action="store", type="choice", dest="loglevel",
            choices=["critical", "error", "warning", "info", "debug"],
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            help="Logging level: critical, error, warning, info, debug "
                 "[default: %default]"
        ),
        make_option(
            "--env",
            action="store", dest="env",
            default=os.environ.get("NOC_ENV", ""),
            help="NOC environment name"
        ),
        make_option(
            "--dc",
            action="store", dest="dc",
            default=os.environ.get("NOC_DC", ""),
            help="NOC datacenter name"
        ),
        make_option(
            "--node",
            action="store", dest="node",
            default=os.environ.get("NOC_NODE", ""),
            help="NOC node name"
        ),
        make_option(
            "--config",
            action="store", dest="conf",
            default=os.environ.get("NOC_CONF", ""),
            help="Comma-separated paths to config in Consul KV-store"
        ),
        make_option(
            "--session-ttl",
            action="store", dest="session_ttl", type="int",
            default=os.environ.get("NOC_SESSION_TTL", "10"),
            help="Leader session ttl"
        )
    ]

    pooled_option_list = [
        make_option(
            "--pool",
            action="store", dest="pool",
            default=os.environ.get("NOC_POOL", "default"),
            help="Pool name"
        )
    ]

    # Service-specific option list
    service_option_list = []
    # Dict parameter containing values accepted
    # via dynamic configuration
    config_interface = {
        "loglevel": StringParameter(
            default=os.environ.get("NOC_LOGLEVEL", "info"),
            choices=["critical", "error", "warning", "info", "debug"]
        )
    }

    ## List of ServiceAPI instances
    api = [
        MonAPI
    ]

    LOG_FORMAT = "%(asctime)s [%(name)s] %(message)s"

    LOG_LEVELS = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG
    }

    def __init__(self):
        self.ioloop = None
        self.logger = None
        self.config = None
        self.consul = None
        self.nsq_writer = None
        self.service_id = str(uuid.uuid4())
        self.leader_group = None
        self.leader_key = None
        self.consul_session = None
        self.renew_session_callback = None

    @property
    def pooled(self):
        if self._pooled is None:
            # Any API with AL_POOL
            self._pooled = any(x for x in self.api
                               if x.level == ServiceAPI.AL_POOL)
        return self._pooled

    @classmethod
    def die(cls, msg):
        sys.stderr.write(str(msg) + "\n")
        sys.stderr.flush()
        sys.exit(1)

    def get_leader_group_name(self, **config):
        """
        Build leader group name
        """
        if self.leader_group_name:
            return self.leader_group_name % config
        else:
            return None

    def parse_bootstrap_config(self):
        """
        Parse CLI command-line options
        """
        opt_list = []
        opt_list += self.option_list
        if self.pooled:
            opt_list += self.pooled_option_list
        opt_list += self.service_option_list
        parser = OptionParser(
            usage=self.usage,
            option_list=opt_list
        )
        try:
            conf, args = parser.parse_args()
        except OptionError, why:
            return self.die(why)
        except OptParseError, why:
            return self.die(why)
        # Get defaults
        vc = DictParameter(attrs=self.config_interface).clean({})
        # Update with bootstrap
        vc.update(vars(conf))
        # Calculate leader group name
        self.leader_group = self.get_leader_group_name(**vc)
        if self.leader_group:
            self.leader_key = "noc/%s/service/leader/%s" % (
                conf.env, self.leader_group
            )
        self.consul = consul.tornado.Consul(
            dc=conf.dc or None
        )
        self.config = Config(
            consul=self.consul,
            interface=DictParameter(attrs=self.config_interface,
                                    truncate=True),
            **vc
        )

    def setup_logging(self):
        if len(logging.root.handlers):
            # Logger is already initialized
            fmt = logging.Formatter(self.LOG_FORMAT, None)
            for h in logging.root.handlers:
                h.setFormatter(fmt)
            logging.root.setLevel(self.LOG_LEVELS[self.config.loglevel])
        else:
            # Imitialize logger
            logging.basicConfig(
                stream=sys.stdout,
                format=self.LOG_FORMAT,
                level=self.LOG_LEVELS[self.config.loglevel]
            )
        self.logger = logging.getLogger(self.name)

    def on_change_loglevel(self, sender, value):
        if value not in self.LOG_LEVELS:
            self.logger.error("Invalid loglevel '%s'. Ignoring", value)
            return
        self.logger.warn("Changing loglevel to %s", value)
        logging.getLogger().setLevel(self.LOG_LEVELS[value])

    @tornado.gen.coroutine
    def renew_session(self):
        """
        Renew Consul Session
        """
        # @todo: Release leadership and terminate
        if self.consul_session:
            try:
                yield self.consul.session.renew(self.consul_session)
            except consul.base.NotFound:
                # Wake up after suspend
                self.die("Wake up after suspend. Restarting")
                self.stop()

    @tornado.gen.coroutine
    def acquire_leadership(self):
        if self.leader_group:
            self.logger.info("Creating Consul session")
            self.consul_session = yield self.consul.session.create(
                name=self.service_id,
                lock_delay=1,
                ttl=self.config.session_ttl
            )
            self.renew_session_callback = tornado.ioloop.PeriodicCallback(
                self.renew_session,
                self.config.session_ttl * 500,
                self.ioloop
            )
            self.renew_session_callback.start()
            self.logger.info("Acquiring leadership for %s (session %s)",
                             self.leader_group, self.consul_session)
            while True:
                try:
                    r = yield self.consul.kv.put(
                        self.leader_key, self.consul_session,
                        acquire=self.consul_session
                    )
                except consul.base.Timeout:
                    continue
                if r:
                    self.logger.info("Leadership acquired")
                    break
                else:
                    # Waiting for change
                    index = None
                    while True:
                        try:
                            index, data = yield self.consul.kv.get(
                                self.leader_key,
                                index=index
                            )
                        except consul.base.Timeout:
                            continue
                        if data and not data.get("Session"):
                            break
        yield self.activate()

    @tornado.gen.coroutine
    def release_leadership(self):
        self.logger.info("Releasing leadership for %s",
                         self.leader_group)
        try:
            yield self.consul.kv.put(
                self.leader_key, "EMPTY",
                release=self.consul_session
            )
        except consul.base.Timeout:
            pass
        self.logger.info("Closing Consul session %s",
                         self.consul_session)
        cs, self.consul_session = self.consul_session, None
        yield self.consul.session.destroy(cs)

    def on_config_ready(self, *args, **kwargs):
        """
        Called when config is ready
        """
        self.logger.info("Config ready")
        if self.leader_group:
            self.ioloop.add_callback(self.acquire_leadership)
        else:
            self.ioloop.add_callback(self.activate)

    def start(self):
        """
        Run main server loop
        """
        self.parse_bootstrap_config()
        self.setup_logging()
        signal.signal(signal.SIGTERM, self.on_SIGTERM)
        if self.pooled:
            self.logger.warn("Running service %s (pool: %s)",
                             self.name, self.config.pool)
        else:
            self.logger.warn("Running service %s", self.name)
        self.ioloop = ioloop.IOLoop.instance()
        # Subscribing to config changes
        for d in dir(self):
            if d.startswith("on_change_"):
                v = d[10:]
                self.logger.debug("Subscribing to changes of %s", v)
                self.config.change.connect(
                    getattr(self, d),
                    sender=v
                )
        #
        self.config.ready.connect(self.on_config_ready)
        self.logger.warn("Starting IOLoop")
        try:
            self.ioloop.start()
        except KeyboardInterrupt:
            self.logger.warn("Interrupted by Ctrl+C")
        finally:
            self.logger.warn("Terminating service %s", self.name)

    def stop(self):
        self.logger.warn("Stopping")
        self.ioloop.add_callback(self.deactivate)

    def on_SIGTERM(self, signo, frame):
        self.logger.warn("SIGTERM caught, Stopping")
        self.stop()

    @tornado.gen.coroutine
    def activate(self):
        """
        Initialize services before run
        """
        self.logger.info("Activating service")
        if self.api:
            # Bind random socket
            socks = tornado.netutil.bind_sockets(0,
                                                 family=socket.AF_INET)
            host, port = socks[0].getsockname()
            if host == "0.0.0.0" or host == "127.0.0.1":
                # Detect advertised address
                aconf = yield self.consul.agent.self()
                ac = aconf["Config"]
                host = ac["ClientAddr"]
                if host == "127.0.0.1":
                    host = ac["AdvertiseAddrWan"]
            self.logger.info("Running HTTP APIs at http://%s:%s/",
                             host, port)
            # Collect and register exposed API
            api = []
            for a in self.api:
                url = a.get_service_url()
                self.logger.info("Supported API: %s at %s",
                                 a.name, url)
                api += [
                    (
                        url,
                        a.get_http_request_handler(),
                        {"service": self, "api_class": a}
                    )
                ]
                if a.level != ServiceAPI.AL_NONE:
                    srv = ServiceSubscriber(self, a)
                    topic = srv.get_topic()
                    self.logger.info(
                        "Registering NSQ RPC endpoint at %s", topic
                    )
                    self.subscribe(topic, "rpc", srv.on_message)
            api += [("/", DocRequestHandler)]
            app = tornado.web.Application(api)
            http_server = tornado.httpserver.HTTPServer(app)
            http_server.add_socket(socks[0])
            # Register services
            for h in self.api:
                if not h.level == ServiceAPI.AL_NONE:
                    continue
                if h.level == ServiceAPI.AL_POOL:
                    tags = [self.config.pool]
                else:
                    tags = None
                self.logger.info(
                    "Registering service %s at %s:%s (tags: %s)",
                    h.name, host, port, tags
                )
                yield self.consul.agent.service.register(
                    name=h.name,
                    service_id=h.name,
                    address=host,
                    port=port,
                    tags=tags,
                    check=[
                        consul.Check.http(
                            "http://%s:%s/" % (host, port),
                            1, 1
                        )
                    ]
                )
        self.on_activate()

    @tornado.gen.coroutine
    def deactivate(self):
        for h in self.api:
            if h.level == ServiceAPI.AL_NONE:
                continue
            self.logger.info("Deregister service %s", h.name)
            yield self.consul.agent.service.deregister(h.name)
        # Release leadership locj
        if self.leader_group and self.consul_session:
            yield self.release_leadership()
        # Finally stop ioloop
        self.logger.info("Stopping IOLoop")
        self.ioloop.stop()

    def on_activate(self):
        """
        Called when service activated
        """
        pass

    def subscribe(self, topic, channel, handler):
        """
        Subscribe to NSQ topic and channel
        """
        self.logger.debug("Subscribing to %s/%s", topic, channel)
        reader = nsq.Reader(
            topic=topic,
            channel=channel,
            # lookupd_http_addresses=["http://127.0.0.1:4161"],
            nsqd_tcp_addresses=["127.0.0.1:4150"],
            lookupd_poll_interval=15,
            message_handler=handler
        )
        return reader

    def connect_writer(self):
        """
        Connect NSQ reader
        """
        if self.nsq_writer:
            return
        self.logger.info("Opening NSQ writer")
        self.nsq_writer = nsq.Writer(["127.0.0.1:4150"])

    def publish(self, topic, msg):
        """
        Publish to NSQ topic
        """
        def callback(conn, data):
            if isinstance(data, nsq.Error):
                if self.nsq_writer.conns:
                    self.logger.error("Failed to publish: %s", data)
                else:
                    # Retry
                    self.ioloop.add_callback(self.publish, topic, msg)

        # Already connected
        if not isinstance(msg, basestring):
            msg = json.dumps(msg)
        self.nsq_writer.pub(topic, msg, callback=callback)

    def open_rpc(self, api_name, level, env=None, service_name=None,
                 pool=None, dc=None, node=None, version=1):
        topic = ServiceAPI.get_service_topic(
            level=level,
            api_name=api_name,
            env=env or self.config.env,
            service_name=service_name,
            pool=pool or self.config.pool,
            dc=dc or self.config.dc,
            node=node or self.config.node,
            version=version
        )
        self.logger.debug("Opening RPC proxy to %s", topic)
        return RPCProxy(self, topic)
