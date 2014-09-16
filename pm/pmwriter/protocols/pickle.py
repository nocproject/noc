## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PMWriter collector pickle mixin
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import sys
import struct
## NOC modules
from base import PMCollectorTCPSocket
from noc.lib.nbsocket.protocols import Protocol
from ..utils import get_unpickler

logger = logging.getLogger(__name__)


class PickleProtocol(Protocol):
    """
    Python pickle PDUs
    """
    def __init__(self, parent, callback):
        super(PickleProtocol, self).__init__(parent, callback)
        self.unpickler = get_unpickler(
            insecure=self.parent.server.config.getboolean(
                "pickle_listener", "insecure")
        )

    def parse_pdu(self):
        HS = 4
        while len(self.in_buffer) > HS:
            l, = struct.unpack("!L", self.in_buffer[:HS])
            if len(self.in_buffer) < l + HS:
                break
            #try:
            data = self.unpickler.loads(self.in_buffer[HS:l + HS])
            #except:
            #    # Unpickle error
            #    logger.error("Unpickling error")
            #    continue
            for i in data:
                try:
                    metric, (value, timestamp) = i
                    value = float(value)
                    timestamp = float(timestamp)
                except ValueError, why:
                    logger.error("Invalid PDU: %s", why)
                    continue
                yield metric, value, timestamp
            self.in_buffer = self.in_buffer[l + HS:]


class PickleProtocolSocket(PMCollectorTCPSocket):
    protocol_class = PickleProtocol
