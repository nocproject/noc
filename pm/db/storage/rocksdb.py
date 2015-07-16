# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RocksDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import importlib
## Third-party modules
rocksdb = importlib.import_module("rocksdb")
## NOC modules
from base import KVStorage


class RocksDBStorage(KVStorage):
    name = "rocksdb"
    prefix_extractor = None

    def __init__(self, database, partition):
        super(RocksDBStorage, self).__init__(database, partition)
        self.path = os.path.join("local", self.name,
                                 "%s.db" % self.partition)
        self.db = None
        self.is_empty = None
        if self.prefix_extractor is None:
            self.prefix_extractor = self.get_prefix_extractor(
                database.hash_width
            )

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        if not self.db:
            self.db = self.get_db()
        op = rocksdb.WriteBatch()
        for k, v in batch:
            op.put(k, v)
        self.db.write(op, sync=False)

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        if self.is_empty:
            raise StopIteration
        if not self.db:
            self.is_empty = not os.path.exists(self.path)
            if self.is_empty:
                raise StopIteration
            self.db = self.get_db(read_only=True)
        it = self.db.iteritems()
        try:
            it.seek(start)
        except rocksdb.errors.RocksIOError:
            raise StopIteration  # Sometime raises "file not found"
        for k, v in it:
            if k > end:
                break
            yield k, v

    def get_db(self, read_only=False):
        return rocksdb.DB(
            self.path,
            rocksdb.Options(
                create_if_missing=True,
                keep_log_file_num=10,
                prefix_extractor=self.prefix_extractor
            ),
            read_only=read_only
        )

    def get_prefix_extractor(self, w):
        """
        Returns SliceTransform with static prefix extractor
        """
        class StaticPrefix(rocksdb.interfaces.SliceTransform):
            def name(self):
                return b'static'

            def transform(self, src):
                return (0, w)

            def in_domain(self, src):
                return len(src) >= w

            def in_range(self, dst):
                return len(dst) == w

        return StaticPrefix()

    def get_last_value(self, start, end):
        if self.is_empty:
            return None, None
        if not self.db:
            self.is_empty = not os.path.exists(self.path)
            if self.is_empty:
                return None, None
            self.db = self.get_db(read_only=True)
        it = reversed(self.db.iteritems())
        try:
            it.seek(end)
        except rocksdb.errors.RocksIOError:
            return None, None
        for k, v in it:
            if k <= end:
                return k, v
        return None, None
