# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Fake testing storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
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

    def _gen_value(self):
        return random.random() * 100

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
            v = self._gen_value()
            yield p + struct.pack("!L", s), struct.pack("!d", v)
            s += self.STEP

    def get_db(self):
        time.sleep(self.OPEN_DELAY)
        return 1

    def get_last_value(self, start, end):
        """
        Returns tuple of (key, value) for the last key in (start, end)
        or return None, None when no data found
        """
        return end, struct.pack("!d", self._gen_value())
