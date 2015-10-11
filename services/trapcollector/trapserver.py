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
from noc.core.ioloop.udpserver import UDPServer
from noc.lib.escape import fm_escape
from noc.lib.snmp.trap import decode_trap
from noc.lib.snmp.ber import DecodeError


logger = logging.getLogger(__name__)


class TrapServer(UDPServer):
    def __init__(self, service, io_loop=None):
        super(TrapServer, self).__init__(io_loop)
        self.service = service

    def on_read(self, data, address):
        object = self.service.lookup_object(address[0])
        if not object:
            return  # Invalid event source
        try:
            community, varbinds = decode_trap(data)
        except DecodeError, why:
            logger.error("Failed to decode trap: %s", data.encode("hex"))
            logger.error("Decoder error: %s", why)
            return
        # @todo: Check trap community
        # Get timestamp
        ts = int(time.time())
        # Build body
        body = {
            "source": "SNMP Trap",
            "collector": self.service.config.pool
        }
        body.update(varbinds)
        body = dict((k, fm_escape(body[k])) for k in body)
        self.service.register_message(object, ts, body)
