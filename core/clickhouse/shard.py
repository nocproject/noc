# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Records sharding
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import random
from collections import defaultdict

# Third-party modules
import ujson

# NOC modules
from noc.config import config, CH_UNCLUSTERED, CH_REPLICATED, CH_SHARDED
from noc.core.service.pub import pub


class BaseSharder(object):
    TOPIC = "chwriter"

    def __init__(self, table=None, chunk=None):
        self.table = table
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
                chunk, data = data[: self.chunk], data[self.chunk :]
                yield topic, "%s\n%s" % (self.table, "\n".join(ujson.dumps(s) for s in chunk))
        self.records = defaultdict(list)

    def pub(self):
        for topic, msg in self.iter_msg():
            pub(topic, msg, raw=True)


class ReplicatedSharder(BaseSharder):
    TOPIC = "chwriter-1-%s"

    def __init__(self, table=None, chunk=None):
        super(ReplicatedSharder, self).__init__(table="raw_%s" % table, chunk=chunk)
        self.n_replicas = config.ch_cluster_topology[0].replicas

    def feed(self, records):
        for i in range(self.n_replicas):
            self.records[self.TOPIC % (i + 1)] += records


class ShardingFunction(object):
    DEFAULT_SHARDING_KEY = "managed_object"
    SHARDING_KEYS = {"span": "ctx"}

    def __init__(self, topology=None):
        self.total_weight = 0
        self._get_shards = self._get_sharding_function(topology)

    def __call__(self, table, record):
        """
        Get list of shards for record

        :param table: Table name
        :param record: Record as dict

        :return: List of strings
        """
        key = self.SHARDING_KEYS.get(table, self.DEFAULT_SHARDING_KEY)
        k = record.get(key, None)
        if k is None:
            si = random.randint(0, self.total_weight - 1)
        else:
            si = int(k) % self.total_weight
        return self._get_shards(si)

    def _get_sharding_function(self, topology=None):
        """
        Returns expression to be evaluated for sharding
        Build expression like
        [1, 2] if k < 2 else [3, 4]
        [1, 2] if k < 2 else [3, 4] if k < 3 else [5, 6]
        [1, 2] if k < 2 else [3, 4] if k < 3 else [5, 6] if k < 4 else [7, 8]
        :return:
        """
        topo = topology or config.ch_cluster_topology
        self.total_weight = 0
        w = 0
        f = ""
        tl = len(topo) - 1
        for sn, shard in enumerate(topo):
            channels = ["chwriter-%s-%s" % (sn + 1, r + 1) for r in range(shard.replicas)]
            self.total_weight += shard.weight
            w += shard.weight
            if not f:
                f = "%r if k < %d" % (channels, w)
            elif sn < tl:
                f = "%s else %r if k < %d" % (f, channels, w)
            else:
                f = "%s else %r" % (f, channels)
        if "else" not in f:
            f = "%s else []" % f  # testing stub
        fn = "def _ch_sharding_function(k):\n    return %s" % f
        scope = {}
        exec(compile(fn, "<string>", "exec"), scope)
        return scope["_ch_sharding_function"]


class ShardingSharder(BaseSharder):
    TOPIC = "chwriter-%s-%s"

    get_shard = None

    DEFAULT_SHARDING_KEY = "managed_object"

    SHARDING_KEYS = {"span": "ctx"}

    def __init__(self, table=None, chunk=None):
        super(ShardingSharder, self).__init__(table="raw_%s" % table, chunk=chunk)
        self.get_shards = ShardingFunction()

    def feed(self, records):
        """
        Shard and replicate records

        :param records:
        :return:
        """
        for m in records:
            if not m:
                continue
            for ch in self.get_shards(self.table, m):
                self.records[ch] += [m]


# Initialize
topo = config.get_ch_topology_type()
if topo == CH_UNCLUSTERED:
    Sharder = BaseSharder
elif topo == CH_REPLICATED:
    Sharder = ReplicatedSharder
elif topo == CH_SHARDED:
    Sharder = ShardingSharder
