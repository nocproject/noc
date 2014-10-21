# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Data retrieving and manipulation functions
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import calendar
import bisect
## Third-party modules
import pytz
## NOC modules
from noc.pm.db.base import tsdb


class TimeSeries(list):
    """
    List of [(value, timestamp)]
    """
    def __init__(self, name, start, end, values):
        list.__init__(self, values)
        self.name = name
        self.pathExpression = name
        self.start = start
        self.end = end
        self.slopes = None
        self.tslist = None
        self.vlist = None
        self.has_none = None

    def __repr__(self):
        return "TimeSeries(name=%s, start=%s, end=%s, points=%d)" % (
            self.name, self.start, self.end, len(self))

    def set_name(self, name):
        self.name = name
        self.pathExpression = name

    def interpolate(self, ts):
        """
        Linear interpolation to given timestamp
        """
        ls = len(self)
        if ts < self.start or not ls:
            return None
        if not self.slopes:
            self.tslist = [v[1] for v in self]
            self.vlist = [v[0] for v in self]
            self.slopes = [
                (y2 - y1) / (x2 - x1)
                for x1, x2, y1, y2
                in zip(self.tslist, self.tslist[1:],
                       self.vlist, self.vlist[1:])
            ]
        i = min(bisect.bisect_left(self.tslist, ts), ls - 2)
        return self.vlist[i] + self.slopes[i] * (ts - self.tslist[i])

    @classmethod
    def unique_timestamps(cls, slist):
        tses = set()
        for ts in slist:
            tses.update([v[1] for v in ts])
        return sorted(tses)

    @classmethod
    def fit_map(cls, name, slist, f, safe=False):
        """
        Fit time series and apply function
        Function must be callable of f([v1, .., vn]) -> float
        """
        if len(slist) == 1:
            return [slist[0]]
        values = []
        for ts in cls.unique_timestamps(slist):
            p = [t.interpolate(ts) for t in slist]
            if safe:
                p = [v for v in p if v is not None]
            v = f(p)
            if v is not None:
                values += [(v, ts)]
        return TimeSeries(name, values[0][1], values[-1][1], values)

    def apply(self, f, safe=True):
        """
        In-place apply function to data.
        Function accepts and returns scalar value
        """
        for i, value in enumerate(self):
            v, t = value
            if v is not None or not safe:
                v = f(v)
            self[i] = (v, t)

    def get_info(self):
        """
        Pickle-friendly representation of the series
        """
        return {
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "values": list(self),
        }


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
    for metric in tsdb.find(path):
        values = tsdb.fetch(metric, start, end)
        ts = TimeSeries(metric, start, end, values)
        ts.pathExpression = metric
        series += [ts]
    return series
