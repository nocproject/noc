# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Deferred calls
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
## NOC modules
from noc.core.scheduler.job import Job
from noc.core.scheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)


def call_later(name, delay=None, scheduler="scheduler", **kwargs):
    """
    Run callable *name* in scheduler process
    :param name: Full callable name
    :param delay: delay in seconds
    """
    scheduler = Scheduler(scheduler)
    data = kwargs or {}
    ts = datetime.datetime.now()
    if delay:
        ts += datetime.timedelta(seconds=delay)
    set_op = {
        Job.ATTR_TS: ts
    }
    if data:
        set_op[Job.ATTR_DATA] = data

    q = {
        Job.ATTR_CLASS: "noc.core.scheduler.calljob.CallJob",
        Job.ATTR_KEY: name
    }
    for k in data:
        q["%s.%s" % (Job.ATTR_DATA, k)] = data[k]
    op = {
        "$set": set_op,
        "$setOnInsert": {
            Job.ATTR_STATUS: Job.S_WAIT,
            Job.ATTR_RUNS: 0,
            Job.ATTR_FAULTS: 0,
            Job.ATTR_OFFSET: 0
        }
    }
    logger.info("Delayed call to %s(%s) in %ss", name, data, delay or "0")
    logger.debug("update(%s, %s, upsert=True)", q, op)
    scheduler.get_collection().update(q, op, upsert=True)
