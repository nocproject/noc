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
import random
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

    # Additional sharding hints
    DEFAULT_SHARDING_KEY = "managed_object"

    SHARDING_KEYS = {
        "span": "ctx"
    }

    def __init__(self):
        super(CHReplicatorService, self).__init__()
        self.sharded = False
        # Unsharded configuration
        self.replicate_topics = None
        # Sharded configuration
        self.shard_expr = None
        self.total_weight = None
        # Reporting information
        self.last_ts = None
        self.last_received = 0
        self.last_sent = 0

    @tornado.gen.coroutine
    def on_activate(self):
        self.load_topology()
        report_callback = tornado.ioloop.PeriodicCallback(
            self.report, 10000, self.ioloop
        )
        report_callback.start()
        self.subscribe(
            "chwriter",
            "chwriter",
            self.on_sharded_data if self.sharded else self.on_unsharded_data,
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
        # Prepare data
        data = records.split("\n")
        raw_fields = data[0]
        fields = raw_fields.split(".")
        data = data[1:-1]
        # Get sharding key
        key = self.SHARDING_KEYS.get(data[0], self.DEFAULT_SHARDING_KEY)
        try:
            fn = fields.index(key)
            tw = self.total_weight
            sf = lambda x: int(x.split("\t")[fn]) % tw
        except AttributeError:
            # No sharding key, random sharding
            sf = lambda x: random.randint(0, self.total_weight - 1)
        # Shard and replicate
        feeds = defaultdict(list)
        sx = self.shard_expr
        for row in data:
            sk = sf(row)
            for c in eval(sx, {"k": sk}):
                feeds[c] += [row]
        metrics["records_received"] += len(data)
        writer = self.get_nsq_writer()
        # Send
        for c in feeds:
            f = feeds[c]
            metrics["records_sent"] += len(f)
            msg = "raw_%s\n%s\n" % (raw_fields, "\n".join(f))
            writer.pub(c, msg)
        return True

    def on_unsharded_data(self, message, records, *args, **kwargs):
        """
        Called on new message in unsharded configuration,
        replicate to all topics
        :return:
        """
        c = records.count("\n") - 1
        metrics["records_received"] += c
        writer = self.get_nsq_writer()
        for topic in self.replicate_topics:
            writer.pub(topic, "raw_" + records)
            metrics["records_sent"] += c
        return True

    @tornado.gen.coroutine
    def report(self):
        received = metrics["records_received"].value
        sent = metrics["records_sent"].value
        t = self.ioloop.time()
        if self.last_ts:
            dt = t - self.last_ts
            recv_speed = float(received - self.last_received) / dt
            sent_speed = float(sent - self.last_sent) / dt
            self.logger.info(
                "Receive speed: %.2frecords/sec, Send speed: %.2frecords/sec",
                recv_speed, sent_speed
            )
        self.last_received = received
        self.last_sent = sent
        self.last_ts = t

    def load_topology(self):
        # shard num -> shard weight
        shard_weights = {}
        # shard num -> List of (address, port)
        shard_hosts = defaultdict(list)
        # Load topolocy
        c = connection()
        rows = c.execute("""
            SELECT shard_num, shard_weight, host_address, port
            FROM system.clusters
            WHERE cluster = %s
            ORDER BY shard_num
        """, args=[config.clickhouse.cluster])
        for shard_num, shard_weight, host_address, host_port in rows:
            shard_num = int(shard_num)
            shard_weights[shard_num] = int(shard_weight)
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
            cond = []
            t = 0
            self.total_weight = 0
            for sn in sorted(shard_weights):
                self.logger.info(
                    "Initializing shard %d: Weight=%d, Hosts=%s",
                    sn, shard_weights[sn],
                    ", ".join("%s:%s" % h for h in shard_hosts[sn])
                )
                self.total_weight += shard_weights[sn]
                t += shard_weights[sn]
                cond += [(t, ["chwriter-%s-%s" % h for h in shard_hosts[sn]])]
            # Compile sharded function
            # Build expression like
            # [1, 2] if k < 2 else [3, 4]
            # [1, 2] if k < 2 else [3, 4] if k < 3 else [5, 6]
            # [1, 2] if k < 2 else [3, 4] if k < 3 else [5, 6] if k < 4 else [7, 8]
            f = ""
            c = len(cond) - 1
            for w, r in cond:
                channels = "[%s]" % ", ".join("'%s'" % h for h in r)
                if not f:
                    f = "%s if k < %d" % (channels, w)
                elif c:
                    f = "%s else %s if k < %d" % (f, channels, w)
                else:
                    f = "%s else %s" % (f, channels)
                c -= 1
            self.logger.info("Sharding expression: %s", f)
            self.shard_expr = compile(f, "<string>", "eval")
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
