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

    def __init__(self, database, partition):
        super(RocksDBStorage, self).__init__(database, partition)
        self.path = os.path.join("local", self.name,
                                 "%s.db" % self.partition)
        self.db = None
        self.is_empty = None

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
        # @todo: Apply PrefixExtractor
        it = self.db.iteritems()
        it.seek(start)
        for k, v in it:
            if k > end:
                break
            yield k, v

    def get_db(self, read_only=False):
        return rocksdb.DB(
            self.path,
            rocksdb.Options(create_if_missing=True),
            read_only=read_only
        )
