# ----------------------------------------------------------------------
# ctl endpoints
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import tracemalloc
import asyncio
from io import StringIO

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# NOC modules
from noc.config import config

router = APIRouter()

logger = logging.getLogger("ctl")


@router.post(
    "/api/ctl/prof/start",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def start_prof():
    """
    Start code profiling
    :return:
    """
    import yappi

    if yappi.is_running():
        return "Already running"
    yappi.start()
    return "Profiling started"


@router.post(
    "/api/ctl/prof/stop",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def stop_prof():
    """
    Stop code profiling
    :return:
    """
    import yappi

    if not yappi.is_running():
        return "Not running"
    yappi.stop()
    return "Profiling stopped"


@router.get(
    "/api/ctl/prof/threads",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def get_prof_threads():
    """
    Get running threads info
    :return:
    """
    import yappi

    i = yappi.get_thread_stats()
    out = StringIO()
    i.print_all(out=out)
    return out.getvalue()


@router.get(
    "/api/ctl/prof/funcs",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def get_prof_funcs():
    """
    Get profiler functions statistics
    :return:
    """
    import yappi

    i = yappi.get_func_stats()
    out = StringIO()
    i.print_all(
        out=out,
        columns={
            0: ("name", 80),
            1: ("ncall", 10),
            2: ("tsub", 8),
            3: ("ttot", 8),
            4: ("tavg", 8),
        },
    )
    return out.getvalue()


@router.post(
    "/api/ctl/manhole", response_class=PlainTextResponse, tags=["internal"], include_in_schema=False
)
async def open_manhole():
    """
    Open manhole
    :return:
    """
    import manhole

    mh = manhole.install()
    return mh.uds_name


@router.post(
    "/api/log/inc", response_class=PlainTextResponse, tags=["internal"], include_in_schema=False
)
async def inc_loglevel():
    """
    Increase loglevel
    :return:
    """
    current_level = logging.root.getEffectiveLevel()
    new_level = max(logging.DEBUG, current_level - 10)
    logger.critical("Changing loglevel: %s -> %s", current_level, new_level)
    logging.root.setLevel(new_level)
    return str(new_level)


@router.post(
    "/api/log/dec", response_class=PlainTextResponse, tags=["internal"], include_in_schema=False
)
async def dec_loglevel():
    """
    Decrease loglevel
    :return:
    """
    current_level = logging.root.getEffectiveLevel()
    new_level = min(logging.CRITICAL, current_level + 10)
    logger.critical("Changing loglevel: %s -> %s", current_level, new_level)
    logging.root.setLevel(new_level)
    return str(new_level)


@router.post(
    "/api/forensic/start",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def forensic_start():
    """
    Start forensic logging
    :return:
    """
    if not config.features.forensic:
        logger.critical("Starting forensic logging")
        config.features.forensic = True
        return "true"
    return "false"


@router.post(
    "/api/forensic/stop",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def forensic_stop():
    """
    Stop forensic logging
    :return:
    """
    if config.features.forensic:
        logger.critical("Stopping forensic logging")
        config.features.forensic = False
        return "true"
    return "false"


@router.post(
    "/api/ctl/memtrace/start",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def start_memtrace():
    """
    Start code profiling
    :return:
    """
    from noc.core.service.loader import get_service

    svc = get_service()
    svc.loop.create_task(trace_leak(svc))
    return "Trace Memory Started"


@router.post(
    "/api/ctl/memtrace/stop",
    response_class=PlainTextResponse,
    tags=["internal"],
    include_in_schema=False,
)
async def stop_memtrace():
    """
    Start code profiling
    :return:
    """
    tracemalloc.stop()
    tracemalloc.clear_traces()
    return "Trace Memory Stopped"


async def trace_leak(svc, delay=60, top=20, trace=1):
    """
    :param svc:
    :param delay:
    :param top:
    :param trace:
    :return:
    """
    logger.info("Start trace: delay: %s, top: %s, trace: %s", delay, top, trace)
    tracemalloc.start(25)
    start = tracemalloc.take_snapshot()
    prev = start
    while tracemalloc.is_tracing():  # is_tracing added in python 3.9
        await asyncio.sleep(delay)
        current = tracemalloc.take_snapshot()
        # compare current snapshot to starting snapshot
        stats = current.compare_to(start, "filename")
        # compare current snapshot to current snapshot
        prev_stats = current.compare_to(prev, "lineno")
        svc.logger.info("[memtrace] %s", "-" * 80)
        svc.logger.info("[memtrace] Top Diffs since start")
        # Print top diffs since Start: current_snapshot - start snapshot
        for i, stat in enumerate(stats[:top], 1):
            svc.logger.info("[memtrace|top_diffs|%s] %s", i, str(stat))
        svc.logger.info("[memtrace] Top Incremental")
        # Print top incremental stats: current_snapshot - previous snapshot
        for i, stat in enumerate(prev_stats[:top], 1):
            svc.logger.info("[memtrace|top_incremental|%s] %s", i, str(stat))
        svc.logger.info("[memtrace] Top Current")
        # Print top current stats
        for i, stat in enumerate(current.statistics("filename")[:top], 1):
            svc.logger.info("[memtrace|top_current|%s] %s", i, str(stat))
        traces = current.statistics("traceback")
        for stat in traces[:trace]:
            svc.logger.info(
                "[memtrace|traceback] Memory blocks: %s, size: %s", stat.count, stat.size / 1024
            )
    # Set previous snapshot to current snapshot
    # prev = current
