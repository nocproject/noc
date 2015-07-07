# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Time-series database
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import struct
import hashlib
import logging
import re
import threading
import time
from collections import namedtuple
## Third-party modules
import cachetools
from bson.binary import Binary
## NOC modules
from settings import config
from noc.pm.db.storage.base import KVStorage
from noc.pm.db.partition.base import Partition
from batch import Batch
from noc.lib.nosql import get_db
from noc.lib.modutils import load_name
from noc.lib.text import split_alnum

logger = logging.getLogger(__name__)


class TimeSeriesDatabase(object):
    MIN_TIMESTAMP = 0
    MAX_TIMESTAMP = 0xFFFFFFFF

    rx_variant = re.compile(r"{([^}]*)}")

    def __init__(self):
        self.mhashes = {}  # metric -> metric hash
        #
        self.hash_width = config.getint("pm_storage", "hash_width")
        self.key_mask = "!%dsL" % self.hash_width
        # Set key-value store class
        kvtype = config.get("pm_storage", "type")
        logger.info("Initializing %s storage. %d-byte wide hash",
                    kvtype, self.hash_width)
        self.kvcls = load_name("noc.pm.db.storage", kvtype, KVStorage)
        if not self.kvcls:
            logger.critical("Invalid storage type: '%s'", kvtype)
            raise ValueError("Invalid storage type: '%s'" % kvtype)
        # Set partitioning scheme
        ps = config.get("pm_storage", "partition")
        logger.info("Setting %s partitioning scheme", ps)
        self.partition = load_name("noc.pm.db.partition", ps, Partition)
        # Index collection
        self.metrics = get_db()["noc.ts.metrics"]
        self.metrics_batch = self.metrics.initialize_ordered_bulk_op()
        self.new_metrics = 0
        self.flush_lock = threading.Lock()
        self.epoch = int(
            time.mktime(
                time.strptime(
                    config.get("pm_storage", "epoch"), "%Y-%m-%d"))
        )
        self.zero_hash = Binary("\x00" * self.hash_width)

    def iter_path(self, parent, path, p, rest):
        def has_wildcards(path):
            return "*" in path or "?" in path or "{" in path or "[" in path

        def get_pattern(p):
            def variant(match):
                v = match.group(0)
                return "(?:%s)" % "|".join(v[1:-1].split(","))

            mp = p.replace("*", ".*")
            mp = mp.replace("?", ".")
            mp = self.rx_variant.sub(variant, mp)
            mp += "$"
            return "^" + mp

        if p == "*":
            # Match all
            q = {
                "parent": parent
            }
        elif has_wildcards(p):
            mp = get_pattern(p)
            q = {
                "parent": parent,
                "local": {
                    "$regex": mp
                }
            }
        else:
            # Quick direct descend
            pp = [p]
            while rest and not has_wildcards(rest[0]):
                pp += [rest.pop(0)]
            pp = ".".join(pp)
            if path:
                pp = path + "." + pp
            # Exact match
            if 0 and rest and rest[0] == "*":
                # x.y.z.*
                m = self.metrics.find_one(
                    {"name": pp},
                    {"name": 1, "hash": 1, "_id": 0}
                )
                if not m:
                    raise StopIteration
                q = {"parent": m["hash"]}
                rest = rest[1:]
            else:
                q = {"name": pp}
        for m in self.metrics.find(
                q,
                {"name": 1, "hash": 1, "has_children": 1, "_id": 0}
        ):
            if rest:
                if m["has_children"]:
                    for mm in self.iter_path(m["hash"], m["name"],
                                             rest[0], rest[1:]):
                        yield mm
            else:
                yield IterResult(name=m["name"], has_children=m["has_children"])

    def find(self, path):
        """
        Returns all metrics matching to path
        """
        parts = path.replace(" ", "").split(".")
        return sorted(
            [m.name for m in self.iter_path(self.zero_hash, "", parts[0], parts[1:])],
            key=lambda x: split_alnum(x)
        )

    def find_detail(self, path):
        """
        Find metrics and return IterResult instances
        """
        parts = path.replace(" ", "").split(".")
        return sorted(
            [m for m in self.iter_path(self.zero_hash, "", parts[0], parts[1:])],
            key=lambda x: split_alnum(x.name)
        )

    def fetch(self, metric, start, end):
        """
        Fetch all metric data within interval
        Returns [(time, value)]
        """
        start = max(int(start), self.epoch)
        end = max(int(end), self.epoch)
        if start == end:
            return []
        elif end < start:
            start, end = end, start
        r = []
        for pn, s, e in self.partition.enumerate(start, end):
            partition = self.get_partition_by_name(pn)
            r += [(self.get_value(v), self.get_time(k))
                    for k, v in partition.iterate(
                        self.get_key(metric, max(s, start)),
                        self.get_key(metric, min(e, end)))
            ]
        return r

    def find_and_fetch(self, path, start, end):
        """
        Find all metrics matching path and fetch them
        Returns dict of metric -> [(time, value)]
        """
        metrics = self.find(path)
        r = dict((m, []) for m in metrics)
        for pn, s, e in self.partition.enumerate(start, end):
            partition = self.get_partition_by_name(pn)
            for m in metrics:
                r[m] += [
                    (self.get_value(v), self.get_time(k))
                    for k, v in partition.iterate(
                        self.get_key(m, max(s, start)),
                        self.get_key(m, min(e, end)))
                ]
        return r

    def get_batch(self):
        return Batch(self)

    def _flush(self, data):
        """
        Batch write collected data to KVStore
        """
        with self.flush_lock:
            s = 0
            for pn in data:
                partition = self.get_partition_by_name(pn)
                d = data[pn]
                partition.write(d)
                s += len(d)
            # Update metrics directory
            if self.new_metrics:
                mb = self.metrics_batch
                self.metrics_batch = self.metrics.initialize_unordered_bulk_op()
                self.new_metrics = 0
                mb.execute(0)
        return s

    def metric_hash(self, metric):
        """
        Calculate metric hash
        """
        ma = self.mhashes.get(metric)
        if ma:
            return ma
        ma = hashlib.md5(metric).digest()[:self.hash_width]
        self.mhashes[metric] = ma
        # Check parents
        if "." in metric:
            parent = ".".join(metric.split(".")[:-1])
            ph = Binary(self.metric_hash(parent))  # Update parent hashes
            self.metrics_batch.find({
                "name": parent,
                "$or": [
                    {"has_children": False},
                    {"has_children": {"$exists": False}}
                ]
            }).update({
                "$set": {
                    "has_children": True
                }
            })
        else:
            ph = self.zero_hash
        # Update metrics directory
        self.metrics_batch \
            .find({"name": metric}) \
            .upsert() \
            .update({
                "$setOnInsert": {
                    "hash": Binary(ma),
                    "parent": ph,
                    "local": metric.split(".")[-1],
                    "has_children": False
                }
            })
        self.new_metrics += 1
        return ma

    def get_key(self, metric, timestamp):
        return struct.pack(
            self.key_mask,
            self.metric_hash(metric),
            int(timestamp)
        )

    def get_time(self, key):
        return struct.unpack(self.key_mask, key)[1]

    def get_value(self, value):
        return struct.unpack("!d", value)[0]

    def get_partition(self, timestamp):
        return self.get_partition_by_name(
            self.partition.get_name(timestamp)
        )

    @cachetools.ttl_cache(maxsize=50, ttl=60)
    def get_partition_by_name(self, name):
        logger.debug("Opening partition %s", name)
        return self.kvcls(self, name)

    def has_children(self, name):
        """
        Return True if metric has children
        """
        m = self.metrics.find_one({"name": name})
        if not m:
            return False
        if self.metrics.find_one({"parent": m["hash"]}):
            return True
        else:
            return False

    def get_last_value(self, metric):
        """
        Returns (value, time) with last metric measure
        or (None, None)
        """
        T = 86400
        t = int(time.time()) + 1
        for pn, s, e in reversed(list(self.partition.enumerate(t - T, t))):
            partition = self.get_partition_by_name(pn)
            k, v = partition.get_last_value(
                self.get_key(metric, s),
                self.get_key(metric, e)
            )
            if k:
                return (
                    self.get_value(v),
                    self.get_time(k)
                )
        return None, None

IterResult = namedtuple("IterResult", ["name", "has_children"])

## Singleton
tsdb = TimeSeriesDatabase()
