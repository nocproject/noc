# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syslog Collector
## (RFC3164)
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from noc.lib.nbsocket import ListenUDPSocket
from noc.sa.activator.event_collector import EventCollector


class SyslogCollector(ListenUDPSocket, EventCollector):
    """
    Syslog collector

    Body has following keys: source, facility, severity, message
    """
    name = "SyslogCollector"

    def __init__(self, activator, address, port):
        self.info("Initializing at %s:%s" % (address, port))
        self.collector_signature = "%s:%s" % (address, port)
        ListenUDPSocket.__init__(self, activator.factory, address, port)
        EventCollector.__init__(self, activator)

    def on_read(self, msg, address, port):
        self.debug(msg)
        object = self.map_event(address)
        if not object:
            # Ignore events from unknown sources
            return
        # Convert msg to valid UTF8
        msg = unicode(msg, "utf8", "ignore").encode("utf8")
        # Parse priority
        priority = 0
        if msg.startswith("<"):
            idx = msg.find(">")
            if idx == -1:
                return
            try:
                priority = int(msg[1:idx])
            except ValueError:
                pass
            msg = msg[idx + 1:].strip()
        # Parse HEADER if exists
        ts = int(time.time())
        #
        body = {
            "source": "syslog",
            "collector": self.collector_signature,
            "facility": priority >> 3,
            "severity": priority & 7,
            "message": msg
        }
        self.process_event(ts, object, body)
