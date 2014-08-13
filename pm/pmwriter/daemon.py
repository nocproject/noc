## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-pmwriter daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import inspect
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.nbsocket.socketfactory import SocketFactory
from noc.lib.nbsocket.acceptedtcpsocket import AcceptedTCPSocket
from noc.pm.pmwriter.protocols.line import LineProtocolSocket
from noc.pm.pmwriter.protocols.pickle import PickleProtocolSocket
from noc.pm.models.storagerule import StorageRule
from cache import MetricsCache
from writer import Writer
from noc.pm.storage.base import TimeSeriesDatabase
from noc.settings import config


class PMWriterDaemon(Daemon):
    daemon_name = "noc-pmwriter"

    LISTENERS = {
        "line_listener": LineProtocolSocket,
        "pickle_listener": PickleProtocolSocket
    }

    def __init__(self, *args, **kwargs):
        self.factory = SocketFactory(controller=self)
        self.line_listener = None
        self.pickle_listener = None
        self.storage_rules = {}
        self.default_storage_rule = None
        self.cache = MetricsCache()
        self.writers = []
        self.storage_class = None
        super(PMWriterDaemon, self).__init__(*args, **kwargs)

    def load_config(self):
        super(PMWriterDaemon, self).load_config()
        self.load_storage_rules()
        self.setup_listener("line_listener")
        self.setup_listener("pickle_listener")
        strategy = self.config.get("cache", "drain_strategy")
        logging.info("Setting cache drain strategy to '%s'" % strategy)
        self.cache.set_strategy(strategy)
        if not self.storage_class:
            self.setup_storage_class()
        self.run_writers()

    def run(self):
        logging.info("Running")
        self.factory.run(True)

    def register_metric(self, metric, value, timestamp):
        self.cache.register_metric(metric, value, timestamp)

    def setup_listener(self, name):
        """
        Setup collector listener
        """
        enabled = self.config.getboolean(name, "enabled")
        address = self.config.get(name, "listen")
        port = self.config.getint(name, "port")
        s = getattr(self, name)
        logging.info("Setup listener %s enabled=%s %s:%s" % (name, enabled, address, port))
        if (s and
                ((enabled and (s.address != address or s.port != port)) or
                     not enabled)):
            # Address/port changed
            logging.info("Closing %s" % name)
            s.close()
            setattr(self, name, None)
        if enabled and not s:
            logging.info("Running %s at %s:%s" % (name, address, port))
            sc = self.LISTENERS[name]
            if issubclass(sc, AcceptedTCPSocket):
                # TCP
                s = self.factory.listen_tcp(address, port, sc)
            else:
                # UDP
                pass
            setattr(self, name, s)

    def load_storage_rules(self):
        logging.info("Loading storage rules")
        rules = {}
        self.default_storage_rule = None
        for sr in StorageRule.objects.all():
            r = {
                "retentions": sr.get_retention(),
                "aggregation_method": sr.aggregation_method,
                "xfilesfactor": sr.xfilesfactor,
                "name": sr.name
            }
            rules[sr.name] = r
            if sr.name == "default":
                self.default_storage_rule = r
        if not self.default_storage_rule:
            self.die("No default storage rule")
        self.storage_rules = rules

    def setup_storage_class(self):
        sc = config.get("pm_storage", "type")
        logging.info("Setting storage class to '%s'" % sc)
        m = __import__("noc.pm.storage.%s_storage" % sc, {}, {}, "*")
        for a in dir(m):
            o = getattr(m, a)
            if (inspect.isclass(o) and
                    issubclass(o, TimeSeriesDatabase) and o.name == sc):
                self.storage_class = o
                break
        if not self.storage_class:
            raise ValueError("Invalid storage type '%s'" % sc)

    def run_writers(self):
        if self.writers:
            return
        for i in range(self.config.getint("writer", "workers")):
            logging.info("Running writer instance %d" % i)
            w = Writer(self, i, self.storage_class)
            self.writers += [w]
            w.start()

    def get_storage_rule(self, metric):
        return self.default_storage_rule
