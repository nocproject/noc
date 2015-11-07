#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ping service
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import functools
import time
# Third-party modules
import tornado.ioloop
import tornado.gen
## NOC modules
from noc.core.service.base import Service
from noc.core.ioloop.timers import PeriodicOffsetCallback
from noc.core.ioloop.ping import Ping


class PingService(Service):
    name = "ping"

    #
    leader_group_name = "ping-%(pool)s"
    pooled = True

    def __init__(self):
        super(PingService, self).__init__()
        self.messages = []
        self.send_callback = None
        self.mappings_callback = None
        self.report_invalid_callback = None
        self.source_map = {}  # IP -> {id, interval, status}
        self.ping_tasks = {}  # IP -> PeriodicCallback
        self.omap = None
        self.fmwriter = None
        self.ping = None

    @tornado.gen.coroutine
    def on_activate(self):
        # Open ping sockets
        self.ping = Ping(self.ioloop, tos=self.config.tos)
        # Register RPC aliases
        self.omap = self.open_rpc("omap")
        self.fmwriter = self.open_rpc("fmwriter", pool=self.config.pool)
        # Set event listeners
        self.subscribe("objmapchange.%(pool)s",
                       self.on_object_map_change)
        # Send spooled messages every 250ms
        self.logger.debug("Stating message sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_messages,
            250,
            self.ioloop
        )
        self.send_callback.start()
        # Get object mappings every 300s
        self.logger.debug("Stating object mapping task")
        self.mappings_callback = tornado.ioloop.PeriodicCallback(
            self.get_object_mappings,
            300000,
            self.ioloop
        )
        self.mappings_callback.start()
        self.ioloop.add_callback(self.get_object_mappings)

    def register_message(self, object, timestamp, data):
        """
        Spool message to be sent
        """
        self.messages += [{
            "ts": timestamp,
            "object": object,
            "data": data
        }]

    @tornado.gen.coroutine
    def send_messages(self):
        """
        Periodic task to send collected messages to fmwriter
        """
        if self.messages:
            yield self.fmwriter.events(self.messages, _notify=True)
            self.messages = []

    @tornado.gen.coroutine
    def get_object_mappings(self):
        """
        Periodic task to request object mappings
        """
        self.logger.debug("Requesting object mappings")
        sm = yield self.omap.get_ping_mappings(
            self.config.pool
        )
        #
        xd = set(self.source_map)
        nd = set(sm)
        # delete probes
        for d in xd - nd:
            self.delete_probe(d)
        # create probes
        for d in nd - xd:
            self.create_probe(d, sm[d])
        # update probe
        for d in xd & nd:
            if self.source_map[d]["interval"] != sm[d]["interval"]:
                self.update_probe(d, sm[d])

    def on_object_map_change(self, topic):
        self.logger.info("Object mappings changed. Rerequesting")
        self.ioloop.add_callback(self.get_object_mappings)

    def create_probe(self, ip, data):
        """
        Create new ping probe
        """
        self.logger.info("Create probe: %s (%ds)", ip, data["interval"])
        self.source_map[ip] = data
        pt = PeriodicOffsetCallback(
            functools.partial(self.ping_check, ip),
            data["interval"] * 1000
        )
        pt.start()
        self.ping_tasks[ip] = pt

    def delete_probe(self, ip):
        if ip not in self.source_map:
            return
        self.logger.info("Delete probe: %s", ip)
        pt = self.ping_tasks.pop(ip)
        pt.stop()
        del self.source_map[ip]

    def update_probe(self, ip, data):
        self.logger.info("Update probe: %s (%ds)", ip, data["interval"])
        self.source_map[ip]["interval"] = data["interval"]
        self.ping_tasks[ip].set_callback_time(data["interval"] * 1000)

    @tornado.gen.coroutine
    def ping_check(self, address):
        """
        Perform ping check and set result
        """
        if address not in self.ping_tasks:
            return
        t0 = time.time()
        s = yield self.ping.ping_check(address, count=3)
        smd = self.source_map.get(address)
        if s is not None and smd and s != smd["status"]:
            self.logger.debug("Changing status for %s to %s",
                              address, s)
            smd["status"] = s
            result = "success" if s else "failed"
            self.register_message(
                smd["id"],
                t0,
                {
                    "source": "system",
                    "probe": "ping",
                    "ip": address,
                    "result": result
                }
            )

if __name__ == "__main__":
    PingService().start()
