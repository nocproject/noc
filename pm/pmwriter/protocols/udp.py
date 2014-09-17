## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMWriter collector UDP protocol
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.lib.nbsocket.listenudpsocket import ListenUDPSocket

logger = logging.getLogger(__name__)


class UDPProtocolSocket(ListenUDPSocket):
    """
    <metric> <value> <timestamp>
    """
    def on_read(self, msg, address, port):
        server = self.factory.controller
        for line in msg.splitlines():
            try:
                metric, value, timestamp = line.strip().split()
                value = float(value)
                timestamp = float(timestamp)
            except ValueError, why:
                logger.error("Invalid PDU: %s", why)
                continue  # Invalid PDU
            server.register_metric(metric, value, timestamp)
