# ----------------------------------------------------------------------
# Automation with processed alarm
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import operator
import time
import enum
from dataclasses import dataclass
from typing import List, Optional, Any, Union

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.fm.enum import ActionStatus, AlarmAction
from noc.core.log import PrefixLoggerAdapter
from noc.core.fm.request import AlarmActionRequest, ActionConfig
from noc.core.debug import error_report
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm
from .actionlog import ActionLog, ActionResult
from .alarmaction import AlarmActionRunner


class ItemStatus(enum.Enum):
    """
    Attributes:
        NEW: New items
        CHANGED: Items was changed
        FAIL: Failed when add to escalation
        EXISTS: Escalate over another doc
        REMOVED: Removed from escalation
    """

    NEW = "new"  # new item
    CHANGED = "changed"  # item changed
    FAIL = "fail"  # escalation fail
    EXISTS = "exists"  # Exists on another escalation
    REMOVED = "removed"  # item removed


@dataclass
class Item(object):
    """Over Job Item"""

    #! Replace to alarm List, status
    alarm: Union[ActiveAlarm, ArchivedAlarm]
    status: ItemStatus = ItemStatus.NEW

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        return self.alarm.managed_object

    def get_state(self):
        return {"alarm": self.alarm.id, "status": self.status.value}


@dataclass
class AllowedAction(object):
    action: AlarmAction
    login: Optional[str] = None
    stop_processing: bool = False
    # permission

    @classmethod
    def from_request(cls, req):
        return AllowedAction(action=req.action)


class AlarmJob(object):
    """
    Runtime Alarm Automation
    """

    def __init__(
        self,
        items: List[Item],
        actions: List[ActionLog],
        allowed_actions: Optional[List[AllowedAction]] = None,
        maintenance_policy: str = None,
        # Repeat
        max_repeat: int = 0,
        repeat_delay: int = 60,
        # Span Context
        ctx_id: Optional[int] = None,
        telemetry_sample: Optional[int] = None,
        # Id document
        name: Optional[str] = None,
        id: Optional[str] = None,
        # Debug
        logger: Optional[Any] = None,
        dry_run: bool = False,
        static_delay: Optional[int] = None,
    ):
        self.id = id
        self.name = name
        self.items: List[Item] = items
        self.actions = actions
        self.maintenance_policy = maintenance_policy or "e"
        # OneTime actions
        self.allowed_actions = allowed_actions
        # Repeat
        self.max_repeat = max_repeat
        self.repeat_delay = repeat_delay
        # Span
        self.ctx_id = ctx_id
        self.telemetry_sample = telemetry_sample
        self.dry_run = dry_run
        self.static_delay: Optional[str] = static_delay
        # Stats
        self.alarm_log = []
        # Alarm Severity
        self.logger = logger or PrefixLoggerAdapter(
            logging.getLogger(__name__), f"[{self.id}|{self.alarm}"
        )

    def __str__(self):
        return f"AlarmJob: {self.alarm}"

    @property
    def leader_item(self) -> "Item":
        """Return first item"""
        return self.items[0]

    @property
    def alarm(self) -> ActiveAlarm:
        """Getting document alarm"""
        return self.leader_item.alarm

    def get_lock_items(self):
        """"""
        return [f"a:{self.alarm}"]

    def run(self) -> None:
        """Run job for works"""
        actions = []
        is_end = self.check_end()
        severity = self.alarm.severity
        now = datetime.datetime.now()
        alarm_ctx = self.alarm.get_message_ctx()
        self.logger.info("Start actions at: %s, End Flag: %s", now, is_end)
        runner = AlarmActionRunner(
            self.items, logger=self.logger, allowed_actions=self.allowed_actions
        )
        for aa in sorted(actions[:] + self.actions, key=operator.attrgetter("timestamp")):
            self.logger.debug("[%s] Processed action", aa)
            if aa.status in [ActionStatus.SUCCESS, ActionStatus.FAILED]:
                # Skip already running job
                if self.dry_run:
                    self.logger.debug("[%s] Action already executed. Next...", aa)
                continue
            elif not aa.is_match(severity, now, self.alarm.ack_user):
                # Set Skip (Condition)
                self.logger.debug(
                    "[%s] Action severity condition [%s] not Match. Next...",
                    aa.action,
                    severity,
                )
                continue
            elif is_end and aa.when != "on_end":
                self.logger.debug("[%s] Action execute on End. Next...", aa.action)
                continue
            elif self.dry_run and self.static_delay:
                time.sleep(self.static_delay)
            try:
                r = runner.run_action(
                    aa.action,
                    **aa.get_ctx(
                        document_id=aa.document_id,
                        alarm_ctx=alarm_ctx,
                    ),
                )  # aa.get_ctx for job
            except Exception as e:
                r = ActionResult(status=ActionStatus.FAILED, error=str(e))  # Exception Status
                error_report()
                # Job Status to Exception
            self.logger.info("[%s] Action result: %s", aa, r)
            if aa.repeat_num < self.max_repeat and r.status == ActionStatus.SUCCESS:
                # If Repeat - add action to next on repeat delay
                # Self register actions
                self.actions.append(aa.get_repeat(self.repeat_delay))
            aa.set_status(r)
            # Processed Result
            if aa.stop_processing:
                # Set Stop job status
                break
        self.alarm_log += runner.get_bulk()
        if actions:
            # Split one_time actions/sequenced action
            self.actions = actions + self.actions

    def check_end(self) -> bool:
        return self.alarm.status == "C"

    @classmethod
    def from_request(
        cls,
        req: AlarmActionRequest,
        alarm: Optional[ActiveAlarm] = None,
        dry_run: bool = False,
        sample: int = 0,
        static_delay: Optional[int] = None,
    ) -> "AlarmJob":
        """Create Job from Request"""
        if not alarm and req.item:
            alarm = get_alarm(req.item.alarm)
        if not alarm:
            raise ValueError("Not Found alarm by id: %s", req.item.alarm)
        start = req.start_at or datetime.datetime.now()
        job = AlarmJob(
            # Job Context
            items=[Item(alarm=alarm)],
            name=str(req),
            id=req.id,
            actions=[
                ActionLog.from_request(a, started_at=start, user=req.user, tt_system=req.tt_system)
                for a in req.actions
            ],
            allowed_actions=[AllowedAction.from_request(aa) for aa in req.allowed_actions],
            # Settings
            # maintenance_policy=req.maintenance_policy,
            # Repeat settings
            max_repeat=req.max_repeats,
            repeat_delay=req.repeat_delay,
            # Span
            ctx_id=req.ctx,
            telemetry_sample=sample,
            dry_run=dry_run,
            static_delay=static_delay,
        )
        return job

    @classmethod
    def from_alarm(
        cls,
        alarm: ActiveAlarm,
        dry_run: bool = False,
        sample: int = 0,
        static_delay: Optional[int] = None,
    ) -> "AlarmJob":
        """"""
        # TTSystem
        job = AlarmJob(
            # Job Context
            items=[Item(alarm=alarm)],
            id=ObjectId(),
            actions=[],
            allowed_actions=[
                AllowedAction(action=AlarmAction.ACK),
                AllowedAction(action=AlarmAction.UN_ACK),
            ],
            telemetry_sample=sample,
            dry_run=dry_run,
            static_delay=static_delay,
        )
        return job

    def is_allowed_action(self, action: AlarmAction, user: User):
        """"""
        return True

    def run_action(
        self,
        action: ActionConfig,
        user: Optional[User] = None,
        tt_system: Optional[TTSystem] = None,
        timestamp: Optional[datetime.datetime] = None,
    ):
        """Run action on Job"""
        if not self.is_allowed_action(action.action, user):
            self.logger.info("[%s] No Permission User for Run Action: %s", user, action.action)
            return
        # self.add_action(action, timestamp)
        al = ActionLog.from_request(
            action, started_at=timestamp, user=user, tt_system=tt_system, one_time=True
        )
        self.actions += [al]
        self.run()

    @classmethod
    def ensure_job(cls, tt_id: str) -> Optional["AlarmJob"]:
        """"""
        job = cls.get_by_tt_id(tt_id)
        if job:
            return job
        aa = ActiveAlarm.get_by_tt_id(tt_id)
        if not aa:
            return
        return AlarmJob.from_alarm(aa)

    @classmethod
    def get_by_tt_id(cls, tt_id) -> Optional["AlarmJob"]:
        """Getting Alarm Job by TT ID"""
        return None
