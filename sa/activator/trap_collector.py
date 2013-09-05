# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP Trap Collector
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python module
import time
import logging
## NOC modules
from noc.lib.nbsocket import ListenUDPSocket
from noc.sa.activator.event_collector import EventCollector
from noc.lib.escape import fm_escape
from noc.lib.snmp.trap import decode_trap
from noc.lib.snmp.ber import DecodeError


class TrapCollector(ListenUDPSocket, EventCollector):
    """
    SNMP Trap collector.

    Body structure:
    {
        "source": "SNMP Trap",
        "oid": "trap oid",
        "oid": "value"
        ....
    }
    """
    name = "TrapCollector"

    def __init__(self, activator, address, port, log_traps=False):
        self.info("Initializing at %s:%s" % (address, port))
        self.collector_signature = "%s:%s" % (address, port)
        self.log_traps = log_traps
        ListenUDPSocket.__init__(self, activator.factory, address, port)
        EventCollector.__init__(self, activator)

    def on_read(self, whole_msg, address, port):
        object = self.map_event(address)
        if not object:
            # Skip events from unknown sources
            return
        if self.log_traps:
            self.info("SNMP TRAP: %r" % whole_msg)
        try:
            community, varbinds = decode_trap(whole_msg)
        except DecodeError, why:
            self.error("Failed to decode trap: %r" % whole_msg)
            self.error("Decoder error: %s" % why)
            return
        # @todo: Check trap community
        body = {
            "source":"SNMP Trap",
            "collector": self.collector_signature
        }
        body.update(varbinds)
        body = dict((k, fm_escape(body[k])) for k in body)
        if self.log_traps:
            self.info("DECODED SNMP TRAP: %r" % body)
        self.process_event(int(time.time()), object, body)
