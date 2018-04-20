# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## yearly partitioning scheme
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from base import Partition


class YearlyPartition(Partition):
    name = "yearly"

    @classmethod
    def get_name(cls, timestamp):
        """
        Get partition name for timestamp
        :param timestamp: integer timestamp
        """
        return time.strftime("%Y", time.localtime(timestamp))

    @classmethod
    def enumerate(cls, start, end):
        """
        Yield all partitions from start to end
        :param start: integer start timestamp
        :param end: integer end timestamp
        """
        y0 = time.localtime(start)[0]
        y1 = time.localtime(end)[0]
        for y in range(y0, y1 + 1):
            yield "%04d" % y
