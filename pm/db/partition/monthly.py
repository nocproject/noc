# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## monthly partitioning scheme
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from base import Partition


class MonthlyPartition(Partition):
    name = "monthly"

    @classmethod
    def get_name(cls, timestamp):
        """
        Get partition name for timestamp
        :param timestamp: integer timestamp
        """
        return time.strftime("%Y.%m", time.localtime(timestamp))

    @classmethod
    def enumerate(cls, start, end):
        """
        Yield all partitions from start to end
        Generator yields partition name, start and end timestamps
        :param start: integer start timestamp
        :param end: integer end timestamp
        """
        t0 = time.localtime(start)[0]
        t1 = time.localtime(end)[0]
        y = t0[0]
        m = t0[1]
        s = y * 12 + m - 1
        f = t1[0] * 12 + t1[1] - 1
        while s <= f:
            yield "%04d.%02d" % (y, m)
            if m == 12:
                y += 1
                m = 1
            else:
                m += 1
            s += 1
