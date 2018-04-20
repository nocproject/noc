# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# CLIPS Environment Pool
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import threading
import logging
import re
import itertools
# Third-party modules
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
import clips


logger = logging.getLogger(__name__)


class CLIPSEnv(object):
    """
    CLIPSEnv context manager.
    Using:
    with CLIPSEnv() as env:
        ....
    """
<<<<<<< HEAD
    free_envs = {}
    used_envs = {}
    env_seq = itertools.count()
    semaphore = threading.BoundedSemaphore(
        clips._clips.getMaxEnvironments()
    )
    lock = threading.Lock()
=======
    cond = threading.Condition()
    max_environments = clips._clips.getMaxEnvironments()
    free_envs = {}
    used_envs = {}
    env_seq = 0
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def __init__(self):
        self.env_id = None

    def __enter__(self):
<<<<<<< HEAD
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
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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

<<<<<<< HEAD
# Extension functions
=======
## Extension functions
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

<<<<<<< HEAD
# Initialize environment
=======
## Initialize environment
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
CLIPSEnv.prepare()
