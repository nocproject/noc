## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-pmwriter daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Event
## NOC modules
from noc.lib.daemon import Daemon
from noc.lib.nbsocket.socketfactory import SocketFactory
from noc.lib.nbsocket.acceptedtcpsocket import AcceptedTCPSocket
from protocols.line import LineProtocolSocket
from protocols.pickle import PickleProtocolSocket
from protocols.udp import UDPProtocolSocket
from noc.pm.db.base import tsdb
from writer import Writer


class PMWriterDaemon(Daemon):
    daemon_name = "noc-pmwriter"

    LISTENERS = {
        "line_listener": LineProtocolSocket,
        "pickle_listener": PickleProtocolSocket,
        "udp_listener": UDPProtocolSocket
    }

    METRICS = [
        "metrics.register",
        "db.flush.ops",
        "db.flush.records",
        "db.flush.time"
    ]

    def __init__(self, *args, **kwargs):
        self.factory = SocketFactory(controller=self,
                                     tick_callback=self.flush)
        self.line_listener = None
        self.pickle_listener = None
        self.udp_listener = None
        self.writing_batch = None
        self.batch_size = 1000
        self.nb = 0
        self.batch_ready = Event()
        self.writer = None
        self.last_data = 0
        super(PMWriterDaemon, self).__init__(*args, **kwargs)
        self.db = tsdb
        self.batch = self.db.get_batch()

    def load_config(self):
        super(PMWriterDaemon, self).load_config()
        self.setup_listener("line_listener")
        self.setup_listener("pickle_listener")
        self.setup_listener("udp_listener")
        self.run_writer()

    def run(self):
        self.logger.info("Running")
        self.factory.run(True)

    def register_metric(self, metric, value, timestamp):
        self.logger.debug("Register metric %s %s %s",
                          metric, value, timestamp)
        self.batch.write(metric, timestamp, value)
        self.metrics.metrics_register += 1
        self.nb += 1
        if self.nb >= self.batch_size:
            self.flush()

    def flush(self):
        if not self.nb:
            return
        self.logger.debug("Flush")
        self.writing_batch = self.batch
        self.batch = self.db.get_batch()
        self.nb = 0
        self.batch_ready.set()

    def get_batch(self):
        self.batch_ready.wait()
        self.batch_ready.clear()
        return self.writing_batch

    def setup_listener(self, name):
        """
        Setup collector listener
        """
        enabled = self.config.getboolean(name, "enabled")
        address = self.config.get(name, "listen")
        port = self.config.getint(name, "port")
        s = getattr(self, name)
        self.logger.info("Setup listener %s enabled=%s %s:%s",
                         name, enabled, address, port)
        if (s and
                ((enabled and (s.address != address or s.port != port)) or
                     not enabled)):
            # Address/port changed
            self.logger.info("Closing %s" % name)
            s.close()
            setattr(self, name, None)
        if enabled and not s:
            self.logger.info("Running %s at %s:%s",
                             name, address, port)
            sc = self.LISTENERS[name]
            if issubclass(sc, AcceptedTCPSocket):
                # TCP
                s = self.factory.listen_tcp(address, port, sc)
            else:
                # UDP
                s = UDPProtocolSocket(self.factory, address, port)
            setattr(self, name, s)

    def run_writer(self):
        if self.writer:
            return
        self.writer = Writer(self)
        self.writer.start()
