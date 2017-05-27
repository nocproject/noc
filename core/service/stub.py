# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service stub for scripts and commands
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import threading
from collections import defaultdict
# Third-party modules
import tornado.ioloop
# NOC modules
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from .rpc import RPCProxy
from .config import Config
from noc.core.perf import metrics


class ServiceStub(object):
    name = "stub"
    pooled = False

    def __init__(self):
        self.logger = logging.getLogger("stub")
        self.perf_metrics = metrics
        self.is_ready = threading.Event()
        self.config = None
        self.ch_metrics = defaultdict(list)

    def start(self):
        t = threading.Thread(target=self._start)
        t.setDaemon(True)
        t.start()

    def _start(self):
        self.config = Config(self)
        self.config.load()
        self.ioloop = tornado.ioloop.IOLoop.instance()
        # Initialize DCS
        self.dcs = get_dcs(DEFAULT_DCS)
        # Activate service
        self.logger.warn("Activating service")
        self.logger.warn("Starting IOLoop")
        self.ioloop.add_callback(self.is_ready.set)
        self.ioloop.start()

    def open_rpc(self, name, pool=None, sync=False, hints=None):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc, sync=sync, hints=hints)

    def iter_rpc_retry_timeout(self):
        """
        Yield timeout to wait after unsuccessful RPC connection
        """
        for t in self.config.rpc_retry_timeout.split(","):
            yield float(t)

    def register_ch_metrics(self, fields, data):
        self.ch_metrics[fields] += data
