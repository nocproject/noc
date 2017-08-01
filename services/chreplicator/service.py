#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# chreplicator service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
# Third-party modules
import tornado.ioloop
import tornado.gen
# NOC modules
from noc.core.service.base import Service
from noc.core.perf import metrics
from noc.config import config
from noc.core.clickhouse.connect import connection


class CHReplicatorService(Service):
    name = "chreplicator"
    require_nsq_writer = True

    def __init__(self):
        super(CHReplicatorService, self).__init__()
        self.sharded = False
        # Unsharded configuration
        self.replicate_topics = None
        # Sharded configuration

    @tornado.gen.coroutine
    def on_activate(self):
        self.load_topology()
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 10000, self.ioloop
        )
        report_callback.start()
        self.subscribe(
            self.topic,
            "chwriter",
            self.on_sharderd_data if self.sharded else self.on_unsharded_data,
            raw=True,
            max_backoff_duration=3
        )

    def on_sharded_data(self, message, records, *args, **kwargs):
        """
        Called on new message in sharded configuration
        Message format
        <table>.<field1>. .. .<fieldN>\n
        <v1>\t...\t<vN>\n
        ...
        <v1>\t...\t<vN>\n

        :param message:
        :param records:
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    def on_unsharded_data(self, message, records, *args, **kwargs):
        """
        Called on new message in unsharded configuration,
        replicate to all topics
        :return:
        """
        for topic in self.replicate_topics:
            self.pub(topic, records)
        return True

    def on_data(self, message, records, *args, **kwargs):
        """
        Called on new dispose message
        Message format
        <table>.<field1>. .. .<fieldN>\n
        <v1>\t...\t<vN>\n
        ...
        <v1>\t...\t<vN>\n
        """
        if metrics["records_buffered"].value > config.chreplicator.records_buffer:
            self.logger.info(
                "Input buffer is full (%s/%s). Deferring message",
                metrics["records_buffered"].value,
                config.chreplicator.records_buffer
            )
            metrics["deferred_messages"] += 1
            return False
        fields, data = records.split("\n", 1)
        channel = self.get_channel(fields)
        n = channel.feed(data)
        metrics["records_received"] += n
        metrics["records_buffered"] += n
        return True

    @tornado.gen.coroutine
    def report(self):
        nm = metrics["records_written"].value
        t = self.ioloop.time()
        if self.last_ts:
            speed = float(nm - self.last_metrics) / (t - self.last_ts)
            self.logger.info(
                "Feeding speed: %.2frecords/sec, active channels: %s, buffered records: %d",
                speed,
                metrics["channels_active"],
                metrics["records_buffered"].value
            )
        self.last_metrics = nm
        self.last_ts = t

    def load_topology(self):
        # shard num -> shard weight
        shard_weights = {}
        # shard num -> List of (address, port)
        shard_hosts = defaultdict(list)
        # Load topolocy
        c = connection()
        rows = c.execute("""
            SELECT shard_num, shard_weight, host_address, host_port
            FROM system.clusters
            WHERE cluster = %s
        """, args=[config.clickhouse.cluster])
        for shard_num, shard_weight, host_address, host_port in rows:
            shard_weights[shard_num] = shard_weight
            shard_hosts[shard_num] += [(host_address, host_port)]
        # Check for distributed topolocy
        if len(shard_weights) == 0:
            self.logger.error("Not-distributed topology. chreplicator is not neededed")
            return
        elif len(shard_weights) == 1:
            # Check for non-sharding topology
            self.logger.info("Non-sharded topology")
            self.sharded = False
        else:
            self.logger.info("Sharded topology")
            self.sharded = True
        if self.sharded:
            # Sharded topology
            total_weight = 0
            for sn in sorted(shard_weight):
                self.logger.info(
                    "Initializing shard %d: Weight=%s, Hosts=%s",
                    sn, shard_weights[sn],
                    ", ".join("%s:%s" % h for h in shard_hosts[sn])
                )
                total_weight +=  shard_weights[sn]
            # @todo: Compile sharded function
        else:
            # Non-sharded topolocy
            sn = list(shard_weights)[0]
            self.logger.info(
                "Replicating to hosts: %s" % ", ".join("%s:%s" % h for h in shard_hosts[sn])
            )
            self.replicate_topics = [
                "chwriter-%s-%s" % (h[0], h[1])
                for h in shard_hosts[sn]
            ]

if __name__ == "__main__":
    CHReplicatorService().start()
