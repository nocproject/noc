# -*- coding: utf-8 -*-
# #----------------------------------------------------------------------
## Carbon-compatible data hooks
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
import calendar
## Third-party modules
import pytz
## NOC modules
from noc.pm.db.base import tsdb


class TimeSeries(list):
    def __init__(self, name, start, end, step, values, consolidate='average'):
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
        if self.consolidationFunc == 'sum':
            return sum(usable)
        if self.consolidationFunc == 'average':
            return float(sum(usable)) / len(usable)
        if self.consolidationFunc == 'max':
            return max(usable)
        if self.consolidationFunc == 'min':
            return min(usable)
        raise Exception("Invalid consolidation function!")

    def __repr__(self):
        return 'TimeSeries(name=%s, start=%s, end=%s, step=%s)' % (
            self.name, self.start, self.end, self.step)


def epoch(dt):
    """
    Returns the epoch timestamp of a timezone-aware datetime object.
    """
    return calendar.timegm(dt.astimezone(pytz.utc).timetuple())


def fetchData(ctx, path):
    """
    Graphite-compatible data-retrieval API
    """
    series = []
    start = int(epoch(ctx["startTime"]))
    end = int(epoch(ctx["endTime"]))
    step = 1
    for metric in tsdb.find(path):
        values = tsdb.fetch(metric, start, end)
        ts = TimeSeries(metric, start, end, step, values)
        ts.pathExpression = metric
        series += [ts]
    return series
