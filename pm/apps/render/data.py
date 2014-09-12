# -*- coding: utf-8 -*-
# #----------------------------------------------------------------------
## Carbon-compatible data hooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from noc.pm.storage.base import TimeSeriesDatabase


class TimeSeries(list):
    def __init__(self, name, start, end, step, values,
                 consolidate="average"):
        list.__init__(self, values)
        self.name = name
        self.start = start
        self.end = end
        self.step = step
        self.consolidationFunc = consolidate
        self.valuesPerPoint = 1
        self.options = {}

    def __iter__(self):
        if self.valuesPerPoint > 1:
            return self.__consolidatingGenerator(list.__iter__(self))
        else:
            return list.__iter__(self)

    def consolidate(self, valuesPerPoint):
        self.valuesPerPoint = int(valuesPerPoint)

    def __consolidatingGenerator(self, gen):
        buf = []
        for x in gen:
            buf.append(x)
            if len(buf) == self.valuesPerPoint:
                while None in buf:
                    buf.remove(None)
                if buf:
                    yield self.__consolidate(buf)
                    buf = []
                else:
                    yield None
        while None in buf:
            buf.remove(None)
        if buf:
            yield self.__consolidate(buf)
        else:
            yield None
        raise StopIteration

    def __consolidate(self, values):
        usable = [v for v in values if v is not None]
        if not usable:
            return None
        if self.consolidationFunc == "sum":
            return sum(usable)
        if self.consolidationFunc == "average":
            return float(sum(usable)) / len(usable)
        if self.consolidationFunc == "max":
            return max(usable)
        if self.consolidationFunc == "min":
            return min(usable)
        raise Exception("Invalid consolidation function!")

    def __repr__(self):
        return "TimeSeries(name=%s, start=%s, end=%s, step=%s)" % (
        self.name, self.start, self.end, self.step)

    def getInfo(self):
        """Pickle-friendly representation of the series"""
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "step": self.step,
            "values": list(self),
        }


# Graphite data retrieval API
def fetchData(ctx, path):
    series = []
    start = int(time.mktime(ctx["startTime"].timetuple()))
    end = int(time.mktime(ctx["endTime"].timetuple()))
    for metric in db.find(path):
        (s, e, step), values = db.fetch(metric, start, end)
        ts = TimeSeries(metric, s, e, step, values)
        ts.pathExpression = metric
        series += [ts]
    return series

##
## Create database instance
##
db = TimeSeriesDatabase.get_database()
