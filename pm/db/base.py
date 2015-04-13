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
import datetime
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
        self.metrics_batch = self.metrics.initialize_unordered_bulk_op()
        self.new_metrics = 0
        self.flush_lock = threading.Lock()
        self.epoch = int(
            time.mktime(
                time.strptime(
                    config.get("pm_storage", "epoch"), "%Y-%m-%d"))
        )
        self.zero_hash = Binary("\x00" * self.hash_width)

    def find(self, path):
        """
        Returns all metrics matching to path
        """
        def has_wildcards(path):
            return "*" in path or "?" in path or "{" in path

        def get_pattern(p):
            def variant(match):
                v = match.group(0)
                return "(?:%s)" % "|".join(v[1:-1].split(","))

            mp = p.replace("*", "[^.]*")
            mp = mp.replace("?", "[^.]")
            mp = self.rx_variant.sub(variant, mp)
            mp += "$"
            return "^" + mp

        def iter_path(parent, path, p, rest):
            q = {
                "parent": parent
            }
            if p == "*":
                pass  # Match all
            elif has_wildcards(p):
                mp = get_pattern(p)
                q["local"] = {
                    "$regex": mp
                }
            elif rest and not has_wildcards(rest[0]):
                # Quick direct descend
                pp = [p]
                while rest and not has_wildcards(rest[0]):
                    pp += [rest.pop(0)]
                pp = ".".join(pp)
                if path:
                    pp = path + "." + pp
                # Exact match
                del q["parent"]
                q["name"] = pp
            else:
                # Exact match
                q["local"] = p
            for m in sorted(self.metrics.find(q, {"name": 1, "hash": 1, "_id": 0}),
                            key=lambda x: split_alnum(x["name"])):
                if rest:
                    for m in iter_path(m["hash"], m["name"], rest[0], rest[1:]):
                        yield m
                else:
                    yield m["name"]

        parts = path.replace(" ", "").split(".")
        return [m for m in iter_path(self.zero_hash, "", parts[0], parts[1:])]

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
            ph = self.metric_hash(parent)  # Update parent hashes
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
                    "local": metric.split(".")[-1]
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

## Singleton
tsdb = TimeSeriesDatabase()
