# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Collector Interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Pythom modules
import time


class EventCollector(object):
    name = "EventCollector"
    INVALID_EVENT_SOURCE_DELAY = 60

    def __init__(self, activator):
        self.activator = activator
        self.invalid_sources = set()
        self.invalid_sources_flush = 0

    def map_event(self, ip):
        """
        Map event source to object
        :param ip: event source
        :return: object id
        """
        t = int(time.time())
        # Append to invalid sources if not passed the check
        object = self.activator.map_event(ip)
        if not object:
            self.invalid_sources.add(ip)
        # Flush all pending invalid event sources
        # when INVALID_EVENT_SOURCE_DELAY interval is expired
        if (self.invalid_sources and
            t - self.invalid_sources_flush >= self.INVALID_EVENT_SOURCE_DELAY):
            self.logger.error("Invalid event sources in last %d seconds: %s",
                self.INVALID_EVENT_SOURCE_DELAY,
                ", ".join(self.invalid_sources))
            for s in self.invalid_sources:
                # Generate "Invalid event source" Event
                self.process_event(t, "", {
                    "source"   : "system",
                    "component": "noc-activator",
                    "activator": self.activator.activator_name,
                    "collector": self.collector_signature,
                    "type"     : "Invalid Event Source",
                    "ip"       : s
                    })
            self.invalid_sources = set()
            self.invalid_sources_flush = t
        return object

    def process_event(self, timestamp, object, body={}):
        self.activator.on_event(timestamp, object, body)
