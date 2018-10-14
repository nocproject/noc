# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Syslog server
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import time
# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.ioloop.udpserver import UDPServer

logger = logging.getLogger(__name__)


class SyslogServer(UDPServer):
    def __init__(self, service, io_loop=None):
        super(SyslogServer, self).__init__(io_loop)
        self.service = service

    def enable_reuseport(self):
        return config.syslogcollector.enable_reuseport

    def enable_freebind(self):
        return config.syslogcollector.enable_freebind

    def on_read(self, data, address):
        metrics["syslog_msg_in"] += 1
        cfg = self.service.lookup_config(address[0])
        if not cfg:
            return  # Invalid event source
        # Convert data to valid UTF8
        data = unicode(data, "utf8", "ignore").encode("utf8")
        # Parse priority
        priority = 0
        if data.startswith("<"):
            idx = data.find(">")
            if idx == -1:
                return
            try:
                priority = int(data[1:idx])
            except ValueError:
                pass
            data = data[idx + 1:].strip()
        # Get timestamp
        ts = int(time.time())
        #
        self.service.register_message(
            cfg, ts, data,
            facility=priority >> 3,
            severity=priority & 7
        )
