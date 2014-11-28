# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## daily partitioning scheme
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from base import Partition


class DailyPartition(Partition):
    name = "daily"

    @classmethod
    def get_name(cls, timestamp):
        """
        Get partition name for timestamp
        :param timestamp: integer timestamp
        """
        return time.strftime("%Y.%m.%d", time.localtime(timestamp))

    @classmethod
    def enumerate(cls, start, end):
        """
        Yield all partitions from start to end
        :param start: integer start timestamp
        :param end: integer end timestamp
        """
        t = start
        while t <= end:
            yield time.strftime("%Y.%m.%d", time.localtime(t))
            t += 86400  # 1 day
