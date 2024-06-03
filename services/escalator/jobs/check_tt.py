# ----------------------------------------------------------------------
# Check TT Job
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import threading
from collections import defaultdict
from typing import Optional, Dict, List, Tuple

# NOC modules
from noc.core.scheduler.job import Job
from noc.core.tt.types import TTAction, TTChange, EscalationStatus, EscalationMember
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.span import Span
from noc.aaa.models.user import User
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.escalation import Escalation
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

    def get_waited_documents(self) -> Dict[str, Escalation]:
        """
        Getting escalated doc
        :return:
        """
        r = {}
        for doc in Escalation.objects.filter(
            escalations__match={
                "member": EscalationMember.TT_SYSTEM.value,
                "key": str(self.object.id),
                "document_id__exists": True,
            },
            end_timestamp__exists=False,
        ):
            item = doc.get_escalation(EscalationMember.TT_SYSTEM, str(self.object.id))
            if item and item.document_id:
                r[item.document_id] = doc
        return r

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
        docs = self.get_waited_documents()
        if not docs:
            return
        changes = defaultdict(list)
        for c in tts.get_updates(
            self.object.last_update_id,
            self.object.last_update_ts,
            list(docs),
        ):
            if c.document_id not in docs:
                self.logger.info(
                    "[%s] Updates on Unknown document with id: %s",
                    c.change_id,
                    c.document_id,
                )
                continue
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
            self.logger.info("Nothing changes...")
            return
        for doc_id, changes in changes.items():
            doc = docs[doc_id]
            with (
                Span(
                    client="escalator",
                    sample=self.object.telemetry_sample,
                    context=doc.ctx_id,
                ) as span_ctx,
                self.lock.acquire(doc.get_lock_items()),
                change_tracker.bulk_changes(),
            ):
                self.processed_changes(doc, changes)
            doc.save()
        if last_ts:
            self.object.register_update(last_ts, last_id)

    def processed_changes(self, doc: Escalation, changes: List[Tuple[User, TTChange]]):
        """
        Processed Alarm Action
        Args:
            doc: Escalation Doc
            changes:
        """
        alarm = doc.alarm
        for user, change in changes:
            action = doc.get_action(change.action, user)
            if action:
                # Already set
                continue
            match change.action:
                case TTAction.CLOSE:
                    alarm.register_clear(
                        f"Clear by TTSystem: {self.object.name}",
                        user=user,
                        timestamp=change.timestamp,
                    )
                case TTAction.ACK:
                    alarm.acknowledge(
                        user, f"Acknowledge by TTSystem: {self.object.name}"
                    )
                case TTAction.UN_ACK:
                    alarm.unacknowledge(
                        user, f"UnAcknowledge by TTSystem: {self.object.name}"
                    )
                case TTAction.NOTIFY:
                    alarm.log_message(change.message, source=str(user))
            doc.set_action(
                action=change.action,
                status=EscalationStatus.OK,
                user=user,
                message=change.message,
            )

    def schedule_next(self, status):
        # Get next run
        if status == self.E_EXCEPTION:
            ts = datetime.datetime.now() + datetime.timedelta(seconds=60)
            self.scheduler.postpone_job(self.attrs[self.ATTR_ID])
        else:
            # Schedule next run
            ts = self.get_next_timestamp(
                config.escalator.wait_tt_check_interval, self.attrs[self.ATTR_OFFSET]
            )
        # Error
        if not ts:
            # Remove disabled job
            self.remove_job()
            return
        self.scheduler.set_next_run(
            self.attrs[self.ATTR_ID], status=status, ts=ts, duration=self.duration
        )
