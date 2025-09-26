# ---------------------------------------------------------------------
# DateTime utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
import bisect

# NOC modules
from noc.core.translation import ugettext as _


def humanize_timedelta(delta):
    def round(x):
        return int(x + 0.5)

    d = delta.days
    s = delta.seconds
    if not d:
        if s < 30:
            return _("less than a minute")
        if s < 90:  # 1:30
            return _("1 minute")
        if s < 2670:  # 44:30
            return _("%d minutes") % round(float(s) / 60.0)
        if s < 5370:  # 1:29:30
            return _("about 1 hour")
        if s < 86370:  # 24:59:30
            return _("about %d hours") % round(float(s) / 3600.0)
        return _("1 day")
    if d == 1 and s < 84600:  # 1D23:59:30
        return _("1 day")
    if d < 30 and s < 84600:  # 29D23:59:30
        return _("%d days") % round((float(d) * 86400.0 + s) / 86400)
    if d < 60 and s < 84600:  # 59D23:59:30
        return _("about 1 month")
    if d < 365:
        return _("%d months") % round(float(d) / 30)
    if d < 446:  # 1Y 3M
        return _("about 1 year")
    if d < 626:  # 1Y 9M
        return _("over 1 year")
    if d < 730:  # 2Y
        return _("almost 2 years")
    n = d // 365
    dd = d - n * 356
    if dd < 446:
        return _("about %d years") % n
    if dd < 626:
        return _("over %d years") % n
    return _("almost %d years") % (n + 1)


def humanize_distance(d):
    try:
        dist = humanize_timedelta(datetime.datetime.now() - d)
    except TypeError:
        dist = _("Never")
    return dist


def total_seconds(td):
    """
    Return total seconds in timedelta object
    :param td: timedelta
    :type td: datetime.timedelta
    :return: seconds
    :rtype: float
    """
    return (td.microseconds + (td.seconds + td.days * 86400) * 1000000) / 1000000.0


def hits_in_range(timestamps, start, stop):
    """
    Count timestamps falling in given range
    :param timestamps: Ordered list of timestamps
    :param start: starting timestamp (datetime)
    :param stop: ending timestamp (datetime)
    :return: Number of hits
    """
    s = bisect.bisect_left(timestamps, start)
    e = bisect.bisect_right(timestamps, stop, s)
    return sum(1 for ts in timestamps[s:e] if start <= ts <= stop)
