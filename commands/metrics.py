# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# metrics uploading
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import random
from collections import defaultdict
# Third-party modules
import nsq
# NOC modules
from noc.core.management.base import BaseCommand
from noc.config import config, CH_UNCLUSTERED, CH_REPLICATED, CH_SHARDED


class Command(BaseCommand):
    TOPIC = "chwriter"
    CHUNK = config.nsqd.ch_chunk_size

    DEFAULT_SHARDING_KEY = "managed_object"

    SHARDING_KEYS = {
        "span": "ctx"
    }


    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd")
        # load command
        load_parser = subparsers.add_parser("load")
        load_parser.add_argument(
            "--fields",
            help="Data fields: <table>.<field1>.<fieldN>"
        )
        load_parser.add_argument(
            "--input",
            help="Input file path"
        )
        load_parser.add_argument(
            "--chunk",
            type=int,
            default=config.nsqd.ch_chunk_size,
            help="Size on chunk"
        )

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_load(self, fields, input, chunk, *args, **kwargs):
        def publish():
            def finish_pub(conn, data):
                if isinstance(data, nsq.Error):
                    self.print("NSQ pub error: %s" % data)
                writer.io_loop.add_callback(publish)

            if not self.records:
                # Done
                writer.io_loop.stop()
                return

            topic = list(self.records)[0]
            d, self.records[topic] = self.records[topic][:self.CHUNK], self.records[topic][self.CHUNK:]
            if not self.records[topic]:
                del self.records[topic]
            msg = "%s\n%s\n" % (self.fields, "\n".join(d))
            writer.pub(topic, msg, callback=finish_pub)

        def on_connect():
            if writer.conns:
                # Connected
                writer.io_loop.add_callback(publish)
            else:
                self.stdout.write("Waiting for NSQ connection\n")
                writer.io_loop.call_later(config.nsqd.connect_timeout,
                                          on_connect)

        # Read data
        with open(input) as f:
            records = f.read().splitlines()
        # Shard incoming data when necessary
        self.fields = fields
        tt = config.get_ch_topology_type()
        if tt == CH_UNCLUSTERED:
            self.process_unclustered(records)
        elif tt == CH_REPLICATED:
            self.process_replicated(records)
        elif tt == CH_SHARDED:
            self.process_sharded(records)
        else:
            raise NotImplementedError()
        # Stream to NSQ
        writer = nsq.Writer([str(a) for a in config.nsqd.addresses])
        writer.io_loop.add_callback(on_connect)
        nsq.run()

    def process_unclustered(self, records):
        self.records[self.TOPIC] = records

    def process_replicated(self, records):
        self.records = {}
        for r in range(config.ch_cluster_topology[0].replicas):
            self.records["chwriter-1-%s" % (r + 1)] = records
        self.fields = "raw_%s" % self.fields

    def process_sharded(self, records):
        # Compile sharding function
        sx = self.get_sharding_function()
        # Get sharding key
        f_parts = self.fields.split(".")
        key = self.SHARDING_KEYS.get(f_parts[0], self.DEFAULT_SHARDING_KEY)
        try:
            fn = f_parts.index(key)
            tw = self.total_weight

            def sf(x):
                return int(x.split("\t")[fn]) % tw

        except AttributeError:
            # No sharding key, random sharding
            def sf(x):
                return random.randint(0, tw - 1)

        # Shards begins with raw_XXX
        self.fields = "raw_%s" % self.fields
        self.records = defaultdict(list)
        # Shard and replicate
        for m in records:
            sk = sf(m)
            # Distribute to channels
            for c in eval(sx, {"k": sk}):
                self.records[c] += [m]

    def get_sharding_function(self):
        """
        Returns expression to be evaluated for sharding
        Build expression like
        [1, 2] if k < 2 else [3, 4]
        [1, 2] if k < 2 else [3, 4] if k < 3 else [5, 6]
        [1, 2] if k < 2 else [3, 4] if k < 3 else [5, 6] if k < 4 else [7, 8]
        :return:
        """
        topo = config.ch_cluster_topology
        self.total_weight = 0
        w = 0
        f = ""
        tl = len(topo) - 1
        for sn, shard in enumerate(topo):
            channels = ["chwriter-%s-%s" % (sn + 1, r + 1)
                        for r in range(shard.replicas)]
            self.total_weight += shard.weight
            w += shard.weight
            if not f:
                f = "%r if k < %d" % (channels, w)
            elif sn < tl:
                f = "%s else %r if k < %d" % (f, channels, w)
            else:
                f = "%s else %r" % (f, channels)
        return compile(f, "<string>", "eval")

if __name__ == "__main__":
    Command().run()
