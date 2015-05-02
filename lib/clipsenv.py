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
    cond = threading.Condition()
    max_environments = clips._clips.getMaxEnvironments()
    free_envs = {}
    used_envs = {}
    env_seq = 0

    def __init__(self):
        self.env_id = None

    def __enter__(self):
        self.cond.acquire()
        env = None
        while not env:
            if self.free_envs:
                # Reuse free environment
                self.env_id, env = self.free_envs.popitem()
                logger.debug("Reusing CLIPS environment #%d", self.env_id)
                self.used_envs[self.env_id] = env
                break
            elif self.env_seq < self.max_environments:
                # Create new environment
                self.env_id = self.env_seq
                self.env_seq += 1
                logger.debug("Creating new CLIPS environment #%d", self.env_id)
                env = clips.Environment()
                self.used_envs[self.env_id] = env
                break
            else:
                logging.debug("No free CLIPS environment available. Waiting")
                self.cond.wait()
        self.cond.release()
        return env

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Releasing CLIPS environment #%d", self.env_id)
        self.cond.acquire()
        env = self.used_envs.pop(self.env_id)
        self.free_envs[self.env_id] = env
        self.env_id = None
        env.Clear()
        env.Reset()
        self.cond.notify()
        self.cond.release()

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
