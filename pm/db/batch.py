## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Batch operation
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import struct


class Batch(object):
    def __init__(self, db):
        self.db = db
        self.data = defaultdict(list)

    def write(self, metric, timestamp, value):
        partition = self.db.partition.get_name(timestamp)
        key = self.db.get_key(metric, timestamp)
        value = struct.pack("!d", value)
        self.data[partition] += [(key, value)]

    def flush(self):
        return self.db._flush(self.data)

    def size(self):
        s = 0
        for p in self.data:
            s += len(self.data[p])
        return s
