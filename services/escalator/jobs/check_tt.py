# ----------------------------------------------------------------------
# Check TT Job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import threading
from collections import defaultdict
from typing import Optional, List, Tuple

# NOC modules
from noc.core.scheduler.job import Job
from noc.core.tt.types import TTAction, TTChange
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.span import Span
from noc.core.fm.request import ActionConfig
from noc.core.fm.enum import AlarmAction
from noc.aaa.models.user import User
from noc.fm.models.ttsystem import TTSystem
from noc.services.correlator.service import AlarmJob
from noc.config import config

RETRY_TIMEOUT = config.escalator.retry_timeout
# @fixme have to be checked
RETRY_DELTA = 60 / max(config.escalator.tt_escalation_limit - 1, 1)
ESCALATION_CHECk_CLOSE_DELAY = 30

retry_lock = threading.Lock()
next_retry = datetime.datetime.now()


class CheckTTJob(Job):
    """
    Check Escalation Document on Remote System on Item with Waited Action
    1. Getting waited docs
    2. Getting it status
    3. Set Escalation Log to Wait
    4. Run escalation job
    TT Adapter API
    # Remove TTL Messages, Max Message ?
    ? Resolve User
    """

    model = TTSystem
    lock = ProcessLock(category="escalator", owner="escalator")
    object: TTSystem

    def resolve_user(self, username: str) -> Optional["User"]:
        """
        Resolve user by TT System Credential

        Args:
            username: User contact id
        """
        return User.get_by_contact(username)

    def handler(self, **kwargs):
        tts = self.object.get_system()
        last_ts: datetime.datetime = datetime.datetime.now()
        last_id: Optional[str] = None
        changes = defaultdict(list)
        for c in tts.get_updates(
            self.object.last_update_id,
            self.object.last_update_ts,
            [],
        ):
            # if c.document_id not in docs:
            #    self.logger.info(
            #        "[%s] Updates on Unknown document with id: %s",
            #        c.change_id,
            #        c.document_id,
            #    )
            #    continue
            user = self.resolve_user(c.user)
            if not user:
                self.logger.info("[%s] Unknown user: %s", c.change_id, c.user)
                continue
            changes[c.document_id] += [(user, c)]
            if c.timestamp:
                last_ts = max(c.timestamp, last_ts)
            if c.change_id:
                last_id = last_id
        if not changes:
            self.logger.debug("Nothing changes...")
            return
        # Request Jobs
        # From alarm (doc) and build jobs
        # Exists Alarm Job / Create from Alarm
        # a_jobs: Dict[str, AlarmJob] = {}
        for doc_id, changes in changes.items():
            a_job = AlarmJob.ensure_job(self.object.get_tt_id(doc_id))
            if not a_job:
                self.logger.info(
                    "[%s] Updates on Unknown document with id: '%s'",
                    "",
                    doc_id,
                )
                continue
            # _job = a_jobs[doc_id]
            with (
                Span(
                    client="escalator",
                    sample=self.object.telemetry_sample,
                    context=a_job.ctx_id,
                ),
                self.lock.acquire(a_job.get_lock_items()),
                change_tracker.bulk_changes(),
            ):
                self.processed_changes(a_job, changes)
            # a_job.save_state()
        if last_ts or last_id:
            self.object.register_update(last_ts, last_id)

    def get_action_config(self, change: TTChange, user: User) -> ActionConfig:
        match change.action:
            case TTAction.CLOSE:
                return ActionConfig(
                    action=AlarmAction.CLEAR,
                    subject=f"Clear by TTSystem: {self.object.name}",
                )
            case TTAction.ACK:
                return ActionConfig(action=AlarmAction.ACK, key=str(user.id))
            case TTAction.UN_ACK:
                return ActionConfig(action=AlarmAction.UN_ACK)
            case TTAction.LOG:
                return ActionConfig(action=AlarmAction.LOG, subject=change.message)

    def processed_changes(self, job: AlarmJob, changes: List[Tuple[User, TTChange]]):
        """
        Processed Alarm Action
        Args:
            job: Escalation Doc
            changes:
        """
        now = datetime.datetime.now()
        for user, change in changes:
            cfg = self.get_action_config(change, user)
            if cfg:
                job.run_action(
                    action=cfg, user=user, tt_system=self.object, timestamp=change.timestamp or now
                )

    def schedule_next(self, status):
        # Get next run
        if status == self.E_EXCEPTION:
            ts = datetime.datetime.now() + datetime.timedelta(seconds=60)
            self.scheduler.postpone_job(self.attrs[self.ATTR_ID])
        else:
            interval = self.object.check_updates_interval or config.escalator.wait_tt_check_interval
            # Schedule next run
            ts = self.get_next_timestamp(interval, self.attrs[self.ATTR_OFFSET])
        # Error
        if not ts:
            # Remove disabled job
            self.remove_job()
            return
        self.scheduler.set_next_run(
            self.attrs[self.ATTR_ID], status=status, ts=ts, duration=self.duration
        )
