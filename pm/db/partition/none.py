# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## none partitioning scheme
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Partition


class NonePartition(Partition):
    name = "none"

    DEFAULT_NAME = "data"

    @classmethod
    def get_name(cls, timestamp):
        """
        Get partition name for timestamp
        :param timestamp: integer timestamp
        """
        return cls.DEFAULT_NAME

    @classmethod
    def enumerate(cls, start, end):
        """
        Yield all partitions from start to end
        Generator yields partition name, start and end timestamps
        :param start: integer start timestamp
        :param end: integer end timestamp
        """
        yield cls.DEFAULT_NAME, start, end
