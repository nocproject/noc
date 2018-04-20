# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BerkeleyDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
import bsddb3
## NOC modules
from base import KVStorage


class BSDDBStorage(KVStorage):
    name = "bsddb"

    def __init__(self, database, partition):
        super(BSDDBStorage, self).__init__(database, partition)
        self.path = os.path.join("local", self.name,
                                 "%s.db" % self.partition)
        self.db = self.get_db()

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        for k, v in batch:
            self.db[k] = v

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        db = self.get_db()
        rec = db.set_location(start)
        while rec:
            if rec[0] > end:
                break
            yield rec
            rec = db.next()

    def get_db(self):
        return bsddb3.btopen(self.path, "c")
