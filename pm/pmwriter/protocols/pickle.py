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
## NOC modules
from base import PMCollectorTCPSocket
from noc.lib.nbsocket.protocols import Protocol
from ..utils import get_unpickler

logger = logging.getLogger(__name__)


class PickleProtocol(Protocol):
    """
    Python pickle PDUs
    """
    MAX_LINE = 1048576

    def parse_pdu(self):
        if len(self.in_buffer) > self.MAX_LINE:
            # Drop long strings
            self.in_buffer = ""
        pdus = self.in_buffer.split("\n")
        self.in_buffer = pdus.pop(-1)
        for pdu in pdus:
            try:
                data = self.parent.unpickler.loads(pdu)
            except:
                # Unpickle error
                logger.error("Unpickling error")
                continue
            for i in data:
                try:
                    metric, (value, timestamp) = i
                    value = float(value)
                    timestamp = float(timestamp)
                except ValueError, why:
                    logger.error("Invalid PDU: %s", why)
                    continue
                yield metric, value, timestamp


class PickleProtocolSocket(PMCollectorTCPSocket):
    protocol_class = PickleProtocol

    def __init__(self, *args, **kwargs):
        super(PickleProtocolSocket, self).__init__(*args, **kwargs)
        self.unpickler = get_unpickler(
            insecure=self.controller.config.getboolean(
                "listen_pickle", "insecure")
        )
