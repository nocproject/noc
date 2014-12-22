## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Key-value storage interface
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

class KVStorage(object):
    """
    Key-value storage partition
    """
    name = None

    def __init__(self, database, partition):
        self.database = database
        self.partition = partition

    def write(self, batch):
        """
        Batch save the data
        """
        raise NotImplementedError()

    def iterate(self, start, end):
        """
        Iterate all keys, values between k0 and k1
        """
        raise NotImplementedError()
