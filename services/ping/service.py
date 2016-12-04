#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ping service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import functools
import time
import datetime
import socket
import struct
import os
# Third-party modules
import tornado.ioloop
import tornado.gen
import tornado.httpclient
## NOC modules
from noc.core.service.base import Service
from noc.core.ioloop.timers import PeriodicOffsetCallback
from noc.core.ioloop.ping import Ping
from probesetting import ProbeSetting


class PingService(Service):
    name = "ping"

    #
    leader_group_name = "ping-%(pool)s"
    pooled = True
    process_name = "noc-%(name).10s-%(pool).3s"
    require_nsq_writer = True

    def __init__(self):
        super(PingService, self).__init__()
        self.messages = []
        self.metrics = []
        self.send_callback = None
        self.mappings_callback = None
        self.metrics_callback = None
        self.probes = {}  # address -> ProbeSetting
        self.omap = None
        self.ping = None

    @tornado.gen.coroutine
    def on_activate(self):
        self.logger.info("Setting nice level to -20")
        try:
            os.nice(-20)
        except OSError as e:
            self.logger.info("Cannot set nice level to -20: %s", e)
        # Open ping sockets
        self.ping = Ping(self.ioloop, tos=self.config.ping.tos)
        # Register RPC aliases
        self.omap = self.open_rpc("omap")
        # Set event listeners
        # self.subscribe("objmapchange.%(pool)s",
        #                self.on_object_map_change)
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
        # Get mappings for the first time
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
        Periodic task to send collected messages to classifier
        """
        if self.messages:
            messages, self.messages = self.messages, []
            self.mpub("events", messages)

    @tornado.gen.coroutine
    def get_object_mappings(self):
        """
        Periodic task to request object mappings
        """
        def is_my_task(d):
            x = struct.unpack("!L", socket.inet_aton(d))[0]
            return x % self.config.global_n_instances == (self.config.instance + self.config.global_offset)

        self.logger.info("Requesting object mappings")
        try:
            sm = yield self.omap.get_ping_mappings(
                self.config.pool
            )
        except self.omap.RPCError as e:
            self.logger.error("Failed to get object mappings: %s", e)
            return
        #
        xd = set(self.probes)
        if self.config.global_n_instances > 1:
            nd = set(x for x in sm if is_my_task(x))
        else:
            nd = set(sm)
        self.logger.info("Processing %d of %d tasks", len(nd), len(sm))
        # delete probes
        for d in xd - nd:
            self.delete_probe(d)
        # create probes
        for d in nd - xd:
            self.create_probe(d, sm[d])
        # update probe
        for d in xd & nd:
            if self.probes[d].is_differ(sm[d]):
                self.update_probe(d, sm[d])
        self.perf_metrics["ping_objects"] = len(self.probes)

    def on_object_map_change(self, topic):
        self.logger.info("Object mappings changed. Rerequesting")
        self.ioloop.add_callback(self.get_object_mappings)

    def create_probe(self, ip, data):
        """
        Create new ping probe
        """
        self.logger.info("Create probe: %s (%ds)", ip, data["interval"])
        ps = ProbeSetting(address=ip, **data)
        self.probes[ip] = ps
        pt = PeriodicOffsetCallback(
            functools.partial(self.ping_check, ps),
            ps.interval * 1000
        )
        ps.task = pt
        pt.start()
        self.perf_metrics["ping_probe_create"] += 1

    def delete_probe(self, ip):
        if ip not in self.probes:
            return
        self.logger.info("Delete probe: %s", ip)
        ps = self.probes[ip]
        ps.task.stop()
        ps.task = None
        del self.probes[ip]
        self.perf_metrics["ping_probe_delete"] += 1

    def update_probe(self, ip, data):
        self.logger.info("Update probe: %s (%ds)", ip, data["interval"])
        ps = self.probes[ip]
        if ps.interval != data["interval"]:
            ps.task.set_callback_time(data["interval"] * 1000)
        self.probes[ip].update(**data)
        self.perf_metrics["ping_probe_update"] += 1

    @tornado.gen.coroutine
    def ping_check(self, ps):
        """
        Perform ping check and set result
        """
        def q(s):
            return s.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

        address = ps.address
        t0 = time.time()
        if address not in self.probes:
            return
        self.perf_metrics["ping_check_total"] += 1
        if ps.time_cond:
            dt = datetime.datetime.fromtimestamp(t0)
            if not eval(ps.time_cond, {"T": dt}):
                self.perf_metrics["ping_check_skips"] += 1
                return
        rtt = yield self.ping.ping_check_rtt(
            address,
            count=self.config.max_packets,
            timeout=self.config.timeout
        )
        s = rtt is not None
        if s:
            self.perf_metrics["ping_check_success"] += 1
        else:
            self.perf_metrics["ping_check_fail"] += 1
        if ps and s != ps.status:
            self.logger.info(
                "[%s] Changing status to %s",
                address, s
            )
            ps.status = s
            result = "success" if s else "failed"
            self.register_message(
                ps.id,
                t0,
                {
                    "source": "system",
                    "probe": "ping",
                    "ip": address,
                    "result": result
                }
            )
        self.logger.debug("[%s] status=%s rtt=%s", address, s, rtt)
        # Send RTT metrics
        if rtt is not None and ps.report_rtt:
            self.register_metrics([
                "Ping\\ |\\ RTT,object=%s value=%s %s" % (
                    q(ps.name), rtt, int(time.time())
                )
            ])

if __name__ == "__main__":
    PingService().start()
