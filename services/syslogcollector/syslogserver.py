# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syslog server
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import time
## NOC modules
from noc.lib.ioloop.udpserver import UDPServer

logger = logging.getLogger(__name__)


class SyslogServer(UDPServer):
    def __init__(self, service, io_loop=None):
        super(SyslogServer, self).__init__(io_loop)
        self.service = service

    def on_read(self, data, address):
        logger.debug("Incoming message: %s %s", data, address)
        #
        object = self.service.lookup_object(address[0])
        if not object:
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
            object, ts, data,
            facility=priority >> 3,
            severity=priority & 7
        )
