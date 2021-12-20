# ----------------------------------------------------------------------
# ctl endpoints
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from io import StringIO

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# NOC modules
from noc.config import config

router = APIRouter()

logger = logging.getLogger("ctl")


@router.post("/api/ctl/prof/start", response_class=PlainTextResponse, tags=["internal"])
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


@router.post("/api/ctl/prof/stop", response_class=PlainTextResponse, tags=["internal"])
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


@router.get("/api/ctl/prof/threads", response_class=PlainTextResponse, tags=["internal"])
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


@router.get("/api/ctl/prof/funcs", response_class=PlainTextResponse, tags=["internal"])
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


@router.post("/api/ctl/manhole", response_class=PlainTextResponse, tags=["internal"])
async def open_manhole():
    """
    Open manhole
    :return:
    """
    import manhole

    mh = manhole.install()
    return mh.uds_name


@router.post("/api/log/inc", response_class=PlainTextResponse, tags=["internal"])
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


@router.post("/api/log/dec", response_class=PlainTextResponse, tags=["internal"])
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


@router.post("/api/forensic/start", response_class=PlainTextResponse, tags=["internal"])
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


@router.post("/api/forensic/stop", response_class=PlainTextResponse, tags=["internal"])
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
