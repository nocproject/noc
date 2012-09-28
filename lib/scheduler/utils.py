# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Scheduler utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from scheduler import Scheduler
from noc.lib.nosql import get_db


def refresh_schedule(scheduler_name, job_class, key, ts=None, delta=None):
    """
    :param scheduler_name:
    :param job_class:
    :param key:
    :param ts:
    :param delta:
    :return:
    """
    if ts is None:
        ts = datetime.datetime.now()
        if delta:
            ts += datetime.timedelta(seconds=delta)
    c = get_db()["noc.schedules.%s" % scheduler_name]
    c.update({
        Scheduler.ATTR_CLASS: job_class,
        Scheduler.ATTR_KEY: key,
        Scheduler.ATTR_STATUS: Scheduler.S_WAIT
    }, {
        "$set": {"ts": ts}
    })
