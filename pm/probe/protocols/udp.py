# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UDP protocol sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## PYthon modules
import logging
## NOC modules
from base import SenderSocket
from noc.lib.nbsocket.udpsocket import UDPSocket

logger = logging.getLogger(__name__)


class UDPProtocolSocket(SenderSocket, UDPSocket):
    name = "udp"
    PDU_CHUNK_SIZE = 10

    def __init__(self, sender, factory, address, port, local_address=None):
        self.addr = (address, port)
        SenderSocket.__init__(self, sender, logger, address, port)
        UDPSocket.__init__(self, factory)

    def flush(self):
        with self.feed_lock:
            while self.data:
                data = self.data[:self.PDU_CHUNK_SIZE]
                self.logger.debug("Sending %d metrics", len(data))
                msg = "".join(
                    "%s %s %s\n" % d for d in data
                )
                self.sendto(msg, self.addr)
                self.data = self.data[self.PDU_CHUNK_SIZE:]
