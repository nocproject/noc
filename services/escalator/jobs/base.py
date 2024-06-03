# ----------------------------------------------------------------------
# Sequence Job Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import threading
from typing import Optional

# NOC modules
from noc.core.scheduler.job import Job
from noc.config import config

RETRY_TIMEOUT = config.escalator.retry_timeout
# @fixme have to be checked
RETRY_DELTA = 60 / max(config.escalator.tt_escalation_limit - 1, 1)
ESCALATION_CHECk_CLOSE_DELAY = 30

retry_lock = threading.Lock()
next_retry = datetime.datetime.now()


class SequenceJob(Job):
    def __init__(self, job, attrs):
        super().__init__(job, attrs)
        self.error: Optional[str] = None

    def schedule_next(self, status):
        # Get next run
        if status == self.E_EXCEPTION:
            ts = datetime.datetime.now() + datetime.timedelta(seconds=60)
            self.scheduler.postpone_job(self.attrs[self.ATTR_ID])
        else:
            ts = self.object.get_next()
        # Error
        if not ts:
            # Remove disabled job
            self.remove_job()
            return
        if self.error:
            error_ts = self.get_next_error_timestamp()
            ts = min(ts, error_ts)
        self.scheduler.set_next_run(
            self.attrs[self.ATTR_ID], status=status, ts=ts, duration=self.duration
        )

    def set_temp_error(self, msg: str):
        """
        Set temporary error on execute

        Args:
            msg: Error description
        """
        self.error = msg

    def get_next_error_timestamp(self, delay: int = None) -> datetime.datetime:
        """
        Reschedule current job and stop escalation

        Args:
            delay:
        """
        global RETRY_DELTA, RETRY_TIMEOUT, next_retry, retry_lock

        self.logger.info("Retry after %ss: %s", delay, self.error)
        now = datetime.datetime.now()
        if delay:
            return now + datetime.timedelta(seconds=delay)
        retry = now + datetime.timedelta(seconds=RETRY_TIMEOUT)
        with retry_lock:
            if retry < next_retry:
                retry = next_retry
            next_retry = retry + datetime.timedelta(seconds=RETRY_DELTA)
        return retry
