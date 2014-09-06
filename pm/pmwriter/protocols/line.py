## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMWriter collector line protocol
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from base import PMCollectorTCPSocket
from noc.lib.nbsocket.protocols import Protocol

logger = logging.getLogger(__name__)


class LineProtocol(Protocol):
    """
    <metric> <value> <timestamp>\n
    """
    def parse_pdu(self):
        pdus = self.in_buffer.split("\n")
        self.in_buffer = pdus.pop(-1)
        for pdu in pdus:
            try:
                metric, value, timestamp = pdu.split()
                value = float(value)
                timestamp = float(timestamp)
            except ValueError, why:
                logger.error("Invalid PDU: %s", why)
                continue  # Invalid PDU
            yield metric, value, timestamp


class LineProtocolSocket(PMCollectorTCPSocket):
    protocol_class = LineProtocol
