#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ping service
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import functools
import time
import datetime
import os
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.config import config
from noc.core.error import NOCError
from noc.core.service.base import Service
from noc.core.ioloop.timers import PeriodicOffsetCallback
from noc.core.ioloop.ping import Ping
from noc.services.ping.probesetting import ProbeSetting
from noc.services.ping.datastream import PingDataStreamClient


class PingService(Service):
    name = "ping"
    #
    leader_group_name = "ping-%(pool)s"
    pooled = True
    require_nsq_writer = True
    process_name = "noc-%(name).10s-%(pool).5s"

    PING_CLS = {
        True: "NOC | Managed Object | Ping OK",
        False: "NOC | Managed Object | Ping Failed"
    }

    def __init__(self):
        super(PingService, self).__init__()
        self.messages = []
        self.send_callback = None
        self.mappings_callback = None
        self.metrics_callback = None
        self.probes = {}  # mo id -> ProbeSetting
        self.omap = None
        self.ping = None
        self.is_throttled = False
        self.slot_number = 0
        self.total_slots = 0

    @tornado.gen.coroutine
    def on_activate(self):
        # Acquire slot
        self.slot_number, self.total_slots = yield self.acquire_slot()
        if self.total_slots > 1:
            self.logger.info(
                "Enabling distributed mode: Slot %d/%d",
                self.slot_number, self.total_slots
            )
        else:
            self.logger.info("Enabling standalone mode")

        self.logger.info("Setting nice level to -20")
        try:
            os.nice(-20)
        except OSError as e:
            self.logger.info("Cannot set nice level to -20: %s", e)
        #
        self.perf_metrics["down_objects"] = 0
        # Open ping sockets
        self.ping = Ping(self.ioloop, tos=config.ping.tos)
        # Send spooled messages every 250ms
        self.logger.debug("Stating message sender task")
        self.send_callback = tornado.ioloop.PeriodicCallback(
            self.send_messages,
            # @fixme have to be configured
            250,
            self.ioloop
        )
        self.send_callback.start()
        # Start tracking changes
        self.ioloop.add_callback(self.get_object_mappings)

    def get_mon_data(self):
        r = super(PingService, self).get_mon_data()
        r["throttled"] = self.is_throttled
        return r

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
            self.mpub("events.%s" % config.pool, messages)

    @tornado.gen.coroutine
    def get_object_mappings(self):
        """
        Subscribe and track datastream changes
        """
        # Register RPC aliases
        client = PingDataStreamClient("cfgping", service=self)
        # Track stream changes
        while True:
            self.logger.info("Starting to track object mappings")
            try:
                yield client.query(
                    limit=config.ping.ds_limit,
                    filters=[
                        "pool(%s)" % config.pool,
                        "shard(%d,%d)" % (self.slot_number, self.total_slots)
                    ],
                    block=1
                )
            except NOCError as e:
                self.logger.info("Failed to get object mappings: %s", e)
                yield tornado.gen.sleep(1)

    def update_probe(self, data):
        if data["id"] in self.probes:
            self._change_probe(data)
        else:
            self._create_probe(data)

    def delete_probe(self, id):
        if id not in self.probes:
            return
        ps = self.probes[id]
        ip = self.probes[id].address
        self.logger.info("Delete probe: %s", ip)
        ps.task.stop()
        ps.task = None
        del self.probes[id]
        self.perf_metrics["ping_probe_delete"] += 1
        if ps.status is not None and not ps.status:
            self.perf_metrics["down_objects"] -= 1
        self.perf_metrics["ping_objects"] = len(self.probes)

    def _create_probe(self, data):
        """
        Create new ping probe
        """
        self.logger.info("Create probe: %s (%ds)", data["address"], data["interval"])
        ps = ProbeSetting(**data)
        self.probes[data["id"]] = ps
        pt = PeriodicOffsetCallback(
            functools.partial(self.ping_check, ps),
            ps.interval * 1000
        )
        ps.task = pt
        pt.start()
        self.perf_metrics["ping_probe_create"] += 1
        self.perf_metrics["ping_objects"] = len(self.probes)

    def _change_probe(self, data):
        self.logger.info("Update probe: %s (%ds)", data["address"], data["interval"])
        ps = self.probes[data["id"]]
        if ps.interval != data["interval"]:
            ps.task.set_callback_time(data["interval"] * 1000)
        ps.update(**data)
        self.perf_metrics["ping_probe_update"] += 1
        self.perf_metrics["ping_objects"] = len(self.probes)

    @tornado.gen.coroutine
    def ping_check(self, ps):
        """
        Perform ping check and set result
        """
        address = ps.address
        t0 = time.time()
        if ps.id not in self.probes:
            return
        self.perf_metrics["ping_check_total"] += 1
        if ps.time_cond:
            dt = datetime.datetime.fromtimestamp(t0)
            if not eval(ps.time_cond, {"T": dt}):
                self.perf_metrics["ping_check_skips"] += 1
                return
        rtt, attempts = yield self.ping.ping_check_rtt(
            ps.address,
            policy=ps.policy,
            size=ps.size,
            count=ps.count,
            timeout=ps.timeout
        )
        s = rtt is not None
        if s:
            self.perf_metrics["ping_check_success"] += 1
        else:
            self.perf_metrics["ping_check_fail"] += 1
        if ps and s != ps.status:
            if s:
                self.perf_metrics["down_objects"] -= 1
            else:
                self.perf_metrics["down_objects"] += 1
            if config.ping.throttle_threshold:
                # Process throttling
                down_ratio = (
                    float(self.perf_metrics["down_objects"]) * 100.0 /
                    float(self.perf_metrics["ping_objects"])
                )
                if self.is_throttled:
                    restore_ratio = config.ping.restore_threshold or config.ping.throttle_threshold
                    if down_ratio <= restore_ratio:
                        self.logger.info(
                            "Leaving throttling mode (%s%% <= %s%%)",
                            down_ratio, restore_ratio
                        )
                        self.is_throttled = False
                        # @todo: Send unthrottling message
                elif down_ratio > config.ping.throttle_threshold:
                    self.logger.info(
                        "Entering throttling mode (%s%% > %s%%)",
                        down_ratio, config.ping.throttle_threshold
                    )
                    self.is_throttled = True
                    # @todo: Send throttling message
            ts = " (Throttled)" if self.is_throttled else ""
            self.logger.info(
                "[%s] Changing status to %s%s",
                address, s, ts
            )
            ps.status = s
        if ps and not self.is_throttled and s != ps.sent_status:
            self.register_message(
                ps.id,
                t0,
                {
                    "source": "system",
                    "$event": {
                        "class": self.PING_CLS[s],
                        "vars": {}
                    }
                }
            )
            ps.sent_status = s
        self.logger.debug("[%s] status=%s rtt=%s", address, s, rtt)
        # Send RTT and attempts metrics
        to_report_rtt = rtt is not None and ps.report_rtt
        if (to_report_rtt or ps.report_attempts) and ps.bi_id:
            lt = time.localtime(t0)
            fields = ["ping", "date", "ts", "managed_object"]
            values = [
                time.strftime("%Y-%m-%d", lt),
                time.strftime("%Y-%m-%d %H:%M:%S", lt),
                str(ps.bi_id)
            ]
            if to_report_rtt:
                fields += ["rtt"]
                values += [str(int(rtt * 1000000))]
            if ps.report_attempts:
                fields += ["attempts"]
                values += [str(attempts)]
            self.register_metrics(
                ".".join(fields),
                ["\t".join(values)]
            )


if __name__ == "__main__":
    PingService().start()
