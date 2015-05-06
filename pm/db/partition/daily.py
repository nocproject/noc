# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## daily partitioning scheme
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
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
        Yield all partitions from start to end.
        Generator yields partition name, start and end timestamps
        :param start: integer start timestamp
        :param end: integer end timestamp
        """
        t = datetime.date.fromtimestamp(start)
        et = datetime.date.fromtimestamp(end)
        day = datetime.timedelta(days=1)
        while t <= et:
            t0 = time.mktime(t.timetuple())
            yield t.strftime("%Y.%m.%d"), t0, t0 + 86399
            t += day
