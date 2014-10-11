# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BerkeleyDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import importlib
## Third-party modules
leveldb = importlib.import_module("leveldb")
## NOC modules
from base import KVStorage


class LevelDBStorage(KVStorage):
    name = "leveldb"

    def __init__(self, database, partition):
        super(LevelDBStorage, self).__init__(database, partition)
        self.path = os.path.join("local", self.name,
                                 "%s.db" % self.partition)
        self.db = self.get_db()

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        op = leveldb.WriteBatch()
        for k, v in batch:
            op.Put(k, v)
        self.db.Write(op, sync=False)

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        for k, v in self.db.RangeIter(start, end, include_value=True):
            yield k, v

    def get_db(self):
        return leveldb.LevelDB(self.path)
