# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service stub for scripts and commands
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import threading
## Third-party modules
import tornado.ioloop
## NOC modules
from noc.core.dcs.loader import get_dcs, DEFAULT_DCS
from .rpc import RPCProxy
from noc.core.perf import metrics


class ServiceStub(object):
    name = "stub"

    def __init__(self):
        self.logger = logging.getLogger("stub")
        self.perf_metrics = metrics

    def start(self):
        t = threading.Thread(target=self._start)
        t.setDaemon(True)
        t.start()

    def _start(self):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        # Initialize DCS
        self.dcs = get_dcs(DEFAULT_DCS)
        # Activate service
        self.logger.warn("Activating service")
        self.logger.warn("Starting IOLoop")
        self.ioloop.start()

    def open_rpc(self, name, pool=None, sync=False):
        """
        Returns RPC proxy object.
        """
        if pool:
            svc = "%s-%s" % (name, pool)
        else:
            svc = name
        return RPCProxy(self, svc, sync)
