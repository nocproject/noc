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
        "$set": {Scheduler.ATTR_TS: ts}
    })


def start_schedule(scheduler_name, job_class, key):
    """
    :param scheduler_name:
    :param job_class:
    :param key:
    :return:
    """
    c = get_db()["noc.schedules.%s" % scheduler_name]
    c.update({
        Scheduler.ATTR_CLASS: job_class,
        Scheduler.ATTR_KEY: key,
        Scheduler.ATTR_STATUS: Scheduler.S_STOP
    }, {
        "$set": {Scheduler.ATTR_STATUS: Scheduler.S_WAIT}
    })


def stop_schedule(scheduler_name, job_class, key):
    """
    :param scheduler_name:
    :param job_class:
    :param key:
    :return:
    """
    c = get_db()["noc.schedules.%s" % scheduler_name]
    c.update({
        Scheduler.ATTR_CLASS: job_class,
        Scheduler.ATTR_KEY: key,
        Scheduler.ATTR_STATUS: Scheduler.S_WAIT
    }, {
        "$set": {Scheduler.ATTR_STATUS: Scheduler.S_STOP}
    })


def submit_job(scheduler_name, job_class, key=None,
               ts=None, delta=None, data=None):
    if ts is None:
        ts = datetime.datetime.now()
        if delta:
            ts += datetime.timedelta(seconds=delta)
    c = get_db()["noc.schedules.%s" % scheduler_name]
    c.insert({
        Scheduler.ATTR_CLASS: job_class,
        Scheduler.ATTR_KEY: key,
        Scheduler.ATTR_STATUS: Scheduler.S_WAIT,
        Scheduler.ATTR_TS: ts,
        Scheduler.ATTR_DATA: data,
        Scheduler.ATTR_SCHEDULE: None
    })


def get_job(scheduler_name, job_class, key=None):
    c = get_db()["noc.schedules.%s" % scheduler_name]
    return c.find_one({
        Scheduler.ATTR_CLASS: job_class, Scheduler.ATTR_KEY: key
    })


def sliding_job(scheduler_name, job_class, key=None,
               ts=None, delta=None, data=None, cutoff_delta=0):
    #
    if ts is None:
        ts = datetime.datetime.now()
        if delta:
            ts += datetime.timedelta(seconds=delta)
    # Check the job exists
    now = datetime.datetime.now()
    c = get_db()["noc.schedules.%s" % scheduler_name]
    j = c.find_one({
        Scheduler.ATTR_CLASS: job_class,
        Scheduler.ATTR_KEY: key
    })
    if j:
        cutoff = j[Scheduler.ATTR_SCHEDULE].get("cutoff")
        if not cutoff or ts <= cutoff:
            # Slide job
            c.update({
                "_id": j["_id"]
            }, {
                "$set": {
                    Scheduler.ATTR_TS: ts
                }
            })
    else:
        # Submit job
        cutoff = now + datetime.timedelta(seconds=cutoff_delta)
        c.insert({
            Scheduler.ATTR_CLASS: job_class,
            Scheduler.ATTR_KEY: key,
            Scheduler.ATTR_STATUS: Scheduler.S_WAIT,
            Scheduler.ATTR_TS: ts,
            Scheduler.ATTR_DATA: data,
            Scheduler.ATTR_SCHEDULE: {
                "cutoff": cutoff
            }
        })


def sync_request(channels, request, object=None, delta=None):
    if not channels:
        return
    data = {
        "request": request
    }
    if object:
        data["object"] = object
    for c in channels:
        sliding_job("main.jobs", "main.sync_request", key=c,
        data=data, delta=delta, cutoff_delta=60)
