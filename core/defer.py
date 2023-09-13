# ----------------------------------------------------------------------
# Deferred calls
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
from typing import Optional
import warnings
import orjson
from threading import Lock

# NOC modules
from noc.core.scheduler.job import Job
from noc.core.scheduler.scheduler import Scheduler
from noc.core.hash import dict_hash_int_args
from noc.core.deprecations import RemovedInNOC2102Warning
from noc.core.service.loader import get_service
from noc.core.ioloop.util import run_sync
from noc.config import config

logger = logging.getLogger(__name__)

DEFAULT_JOB_CLASS = "noc.core.scheduler.calljob.CallJob"


def call_later(
    name: str,
    delay: Optional[float] = None,
    scheduler: str = "scheduler",
    pool: Optional[str] = None,
    job_class: str = DEFAULT_JOB_CLASS,
    shard: Optional[int] = None,
    max_runs: Optional[int] = None,
    **kwargs,
):
    """
    Schedule to run callable *name* in scheduler process
    :param name: Full callable name
    :param delay: delay in seconds
    :param scheduler: Name of scheduler
    :param pool: Pool name
    :param job_class: Job class
    :param shard: Sharding key
    :param max_runs: Maximum amount of retries
    """
    # Check if defer should be used
    if (
        scheduler == "scheduler"
        and not pool
        and job_class == DEFAULT_JOB_CLASS
        and not max_runs
        and not delay
    ):
        warnings.warn(
            "defer should be used instead of call_later. Will be strict requirement in NOC 21.2",
            RemovedInNOC2102Warning,
        )
        # @todo: Really pass to defer?
    scheduler = Scheduler(scheduler, pool=pool)
    data = kwargs or {}
    ts = datetime.datetime.now()
    if delay:
        ts += datetime.timedelta(seconds=delay)
    # Process sharding
    if shard is None:
        shard = dict_hash_int_args(job_class=job_class, name=name, pool=pool, **kwargs)
    shard = (shard if shard >= 0 else -shard) % 0x7FFFFFFF
    #
    set_op = {Job.ATTR_TS: ts}
    iset_op = {
        Job.ATTR_STATUS: Job.S_WAIT,
        Job.ATTR_RUNS: 0,
        Job.ATTR_FAULTS: 0,
        Job.ATTR_OFFSET: 0,
        Job.ATTR_SHARD: shard,
    }
    if max_runs:
        iset_op[Job.ATTR_MAX_RUNS] = max_runs
    if data:
        set_op[Job.ATTR_DATA] = {k: v for k, v in data.items() if not k.startswith("_")}

    q = {Job.ATTR_CLASS: job_class, Job.ATTR_KEY: name}
    for k in list(data):
        if k.startswith("_"):
            # Hidden attribute JobClass, remove it from data
            q[k] = data[k]
            continue
        q["%s.%s" % (Job.ATTR_DATA, k)] = data[k]
    op = {"$set": set_op, "$setOnInsert": iset_op}
    logger.info("Delayed call to %s(%s) in %ss", name, data, delay or "0")
    logger.debug("update(%s, %s, upsert=True)", q, op)
    scheduler.get_collection().update_one(q, op, upsert=True)


JOBS_STREAM = "jobs"
JOBS_PARTITIONS: Optional[int] = None
jp_lock = Lock()


def defer(handler: str, key: Optional[int] = None, **kwargs) -> None:
    """
    Offload job to worker
    :param handler: Full path to callable
    :param key: Sharding key
    :param kwargs: Callable arguments
    :return:
    """
    global JOBS_PARTITIONS, jp_lock

    async def init_partitions():
        global JOBS_PARTITIONS

        JOBS_PARTITIONS = await svc.get_stream_partitions(JOBS_STREAM)

    svc = get_service()
    if JOBS_PARTITIONS is None:
        # Get number of partitions
        with jp_lock:
            if JOBS_PARTITIONS is None:
                run_sync(init_partitions)

    q = [{"handler": handler, "kwargs": kwargs or {}}]
    if key is None:
        key = dict_hash_int_args(handler=handler, **kwargs)
    q = orjson.dumps(q)
    if len(q) > config.msgstream.max_message_size:
        logger.warning("[%s|%s] Defer max message size exceeded: %s", handler, key, len(q))
    svc.publish(q, stream=JOBS_STREAM, partition=key % JOBS_PARTITIONS)
