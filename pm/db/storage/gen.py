# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RocksDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import random
import time
import struct
## NOC modules
from base import KVStorage


class GenStorage(KVStorage):
    name = "gen"
    STEP = 60
    OPEN_DELAY = 0.003
    WRITE_DELAY = 0.001
    READ_DELAY = 0.001

    def __init__(self, database, partition):
        super(GenStorage, self).__init__(database, partition)
        self.db = None

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        time.sleep(self.WRITE_DELAY)

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        if not self.db:
            self.db = self.get_db()

        p = start[:-4]
        s = struct.unpack("!L", start[-4:])[0]
        e = struct.unpack("!L", end[-4:])[0]
        time.sleep(self.READ_DELAY)
        while s <= e:
            v = random.random() * 100
            yield p + struct.pack("!L", s), struct.pack("!d", v)
            s += self.STEP

    def get_db(self):
        time.sleep(self.OPEN_DELAY)
        return 1
