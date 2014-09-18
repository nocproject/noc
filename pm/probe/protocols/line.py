# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Line protocol sender
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from base import SenderSocket
from noc.lib.nbsocket.connectedtcpsocket import ConnectedTCPSocket

logger = logging.getLogger(__name__)


class LineProtocolSocket(SenderSocket, ConnectedTCPSocket):
    name = "line"
    def __init__(self, sender, factory, address, port, local_address=None):
        SenderSocket.__init__(self, sender, logger, address, port)
        ConnectedTCPSocket.__init__(self, factory, address, port, local_address)

    def flush(self):
        with self.feed_lock:
            self.logger.debug("Sending %d metrics", len(self.data))
            data = "".join(
                "%s %s %s\n" % d for d in self.data
            )
            self.write(data)
            self.data = []
