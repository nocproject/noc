# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SNMP Trap Server
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import time
# NOC modules
from noc.core.ioloop.udpserver import UDPServer
from noc.lib.escape import fm_escape
from noc.core.snmp.trap import decode_trap
from noc.config import config
from noc.core.perf import metrics


logger = logging.getLogger(__name__)


class TrapServer(UDPServer):
    def __init__(self, service, io_loop=None):
        super(TrapServer, self).__init__(io_loop)
        self.service = service

    def enable_reuseport(self):
        return config.trapcollector.enable_reuseport

    def enable_freebind(self):
        return config.trapcollector.enable_freebind

    def on_read(self, data, address):
        metrics["trap_msg_in"] += 1
        cfg = self.service.lookup_config(address[0])
        if not cfg:
            return  # Invalid event source
        try:
            community, varbinds = decode_trap(data)
        except ValueError as e:
            metrics["error", ("type", "decode_failed")] += 1
            logger.error("Failed to decode trap: %s", data.encode("hex"))
            logger.error("Decoder error: %s", e)
            return
        # @todo: Check trap community
        # Get timestamp
        ts = int(time.time())
        # Build body
        body = {
            "source": "SNMP Trap",
            "collector": config.pool
        }
        body.update(varbinds)
        body = dict((k, fm_escape(body[k])) for k in body)
        self.service.register_message(cfg.id, ts, body)
