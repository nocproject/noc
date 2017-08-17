# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Records sharding
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import random
from collections import defaultdict
# NOC modules
from noc.config import config, CH_UNCLUSTERED, CH_REPLICATED, CH_SHARDED
from .pub import pub


class BaseSharder(object):
    TOPIC = "chwriter"

    def __init__(self, fields, chunk=None):
        self.fields = fields
        self.records = defaultdict(list)
        self.chunk = chunk or config.nsqd.ch_chunk_size

    def feed(self, records):
        self.records[self.TOPIC] += records

    def iter_msg(self):
        """
        Yields topic, chunk pairs
        :return:
        """
        for topic in self.records:
            data = self.records[topic]
            while data:
                chunk, data = data[:self.chunk], data[self.chunk:]
                yield topic, "%s\n%s\n" % (self.fields, "\n".join(chunk))
        self.records = defaultdict(list)

    def pub(self):
        for topic, msg in self.iter_msg():
            pub(topic, msg, raw=True)


class ReplicatedSharder(BaseSharder):
    TOPIC = "chwriter-1-%s"

    def __init__(self, fields, chunk=None):
        super(ReplicatedSharder, self).__init__(fields, chunk=chunk)
        self.fields = "raw_%s" % fields
        self.n_replicas = config.ch_cluster_topology[0].replicas

    def feed(self, records):
        for i in range(self.n_replicas):
            self.records[self.TOPIC % (i + 1)] += records


class ShardingSharder(BaseSharder):
    TOPIC = "chwriter-%s-%s"

    get_shard = None

    DEFAULT_SHARDING_KEY = "managed_object"

    SHARDING_KEYS = {
        "span": "ctx"
    }

    def __init__(self, fields, chunk=None):
        super(ShardingSharder, self).__init__(fields, chunk=chunk)
        self.f_parts = fields.split(".")
        self.fields = "raw_%s" % fields
        self.total_weight = 0
        if not self.get_shard:
            self.get_shard = self.get_sharding_function()

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

    def feed(self, records):
        key = self.SHARDING_KEYS.get(self.f_parts[0], self.DEFAULT_SHARDING_KEY)
        tw = self.total_weight
        try:
            fn = self.f_parts[1:].index(key)

            def sf(x):
                return int(x.split("\t")[fn]) % tw

        except ValueError:
            # No sharding key, random sharding
            def sf(x):
                return random.randint(0, tw - 1)

        sx = self.get_shard
        # Shard and replicate
        for m in records:
            if not m:
                continue
            sk = sf(m)
            # Distribute to channels
            for c in eval(sx, {"k": sk}):
                self.records[c] += [m]

# Initialize
topo = config.get_ch_topology_type()
if topo == CH_UNCLUSTERED:
    Sharder = BaseSharder
elif topo == CH_REPLICATED:
    Sharder = ReplicatedSharder
elif topo == CH_SHARDED:
    Sharder = ShardingSharder
