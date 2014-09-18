# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Pickle protocol sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from cPickle import dumps
import struct
import logging
## NOC modules
from base import SenderSocket
from noc.lib.nbsocket import ConnectedTCPSocket

logger = logging.getLogger(__name__)


class PickleProtocolSocket(SenderSocket, ConnectedTCPSocket):
    name = "pickle"
    PDU_CHUNK_SIZE = 1000  # Up to 1000 metrics in packet

    def __init__(self, sender, factory, address, port, local_address=None):
        SenderSocket.__init__(self, sender, logger, address, port)
        ConnectedTCPSocket.__init__(self, factory, address, port, local_address)

    def flush(self):
        with self.feed_lock:
            while self.data:
                data = self.data[:self.PDU_CHUNK_SIZE]
                self.logger.debug("Sending %d metrics", len(data))
                p = [
                    (d[0], (d[2], d[1]))
                     for d in data
                ]
                payload = dumps(p, protocol=2)
                header = struct.pack("!L", len(payload))
                self.write(header + payload)
                self.data = self.data[self.PDU_CHUNK_SIZE:]
