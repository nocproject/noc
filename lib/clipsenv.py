# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLIPS Environment Pool
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import threading
import logging
import re
import itertools
## Third-party modules
import clips


logger = logging.getLogger(__name__)


class CLIPSEnv(object):
    """
    CLIPSEnv context manager.
    Using:
    with CLIPSEnv() as env:
        ....
    """
    free_envs = {}
    used_envs = {}
    env_seq = itertools.count()
    semaphore = threading.BoundedSemaphore(
        clips._clips.getMaxEnvironments()
    )
    lock = threading.Lock()

    def __init__(self):
        self.env_id = None

    def __enter__(self):
        self.semaphore.acquire()
        with self.lock:
            if self.free_envs:
                # Free environments are available
                self.env_id, env = self.free_envs.popitem()
                logger.debug("Reusing CLIPS environment #%d", self.env_id)
            else:
                # Create new environment
                self.env_id = self.env_seq.next()
                logger.debug("Creating new CLIPS environment #%d", self.env_id)
                env = clips.Environment()
            self.used_envs[self.env_id] = env
        return env

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.lock:
            logger.debug("Releasing CLIPS environment #%d", self.env_id)
            env = self.used_envs.pop(self.env_id)
            self.free_envs[self.env_id] = env
            self.env_id = None
            env.Clear()
            env.Reset()
        self.semaphore.release()

    @classmethod
    def prepare(cls):
        """
        Prepare CLIPS
        """
        logger.debug("Prepare CLIPS")
        # Install python functions
        logger.debug("Register python function py-match-re")
        clips.RegisterPythonFunction(
            clips_match_re,
            "py-match-re"
        )

## Extension functions
def _clips_bool(r):
    """
    Returns Clips TRUE or FALSE depending of value of r
    """
    if bool(r):
        return CLIPS_TRUE
    else:
        return CLIPS_FALSE


def clips_match_re(rx, s):
    """
    Check string matches regular expression
    Usage:
        (match-re "^\s+test" ?f)
    """
    logger.error("@@@@ MATCH RE: <%s> <%s> -> %s", rx, s, bool(re.search(rx, s)))
    return _clips_bool(re.search(rx, s))


CLIPS_TRUE = clips.Symbol("TRUE")
CLIPS_FALSE = clips.Symbol("FALSE")

## Initialize environment
CLIPSEnv.prepare()
