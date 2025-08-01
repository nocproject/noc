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
from dataclasses import dataclass
from typing import List, Optional, Any, Union, Dict

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.fm.enum import ActionStatus, AlarmAction, ItemStatus
from noc.core.log import PrefixLoggerAdapter
from noc.core.fm.request import AlarmActionRequest, ActionConfig
from noc.core.debug import error_report
from noc.core.scheduler.job import Job
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmwatch import Effect
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm
from .actionlog import ActionLog, ActionResult
from .alarmaction import AlarmActionRunner


@dataclass(repr=True)
class Item(object):
    """Over Job Item"""

    #! Replace to alarm List, status
    alarm: Union[ActiveAlarm, ArchivedAlarm]
    status: ItemStatus = ItemStatus.NEW

    def __str__(self):
        return f"{self.alarm}: {self.status}"

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        return self.alarm.managed_object

    def get_state(self):
        return {"alarm": self.alarm.id, "status": self.status.value}

    @classmethod
    def from_alarm(cls, alarm, is_clear: bool = False) -> "Item":
        """Create Item from Alarm"""
        if is_clear:
            return Item(alarm=alarm, status=ItemStatus.REMOVED)
        return Item(alarm=alarm, status=ItemStatus.from_alarm(alarm))


@dataclass(repr=True)
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
        max_repeats: int = 0,
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
        self.max_repeats = max_repeats
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
        # additional
        return f"AlarmJob: {self.alarm}"

    def __repr__(self):
        return self.__str__()

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
            elif aa.timestamp > now:
                #
                break
            # if not aa.to_run(status, delay):
            #    continue
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
            if aa.repeat_num < self.max_repeats and r.status == ActionStatus.SUCCESS:
                # If Repeat - add action to next on repeat delay
                # Self register actions
                self.actions.append(aa.get_repeat(self.repeat_delay))
            aa.set_status(r)
            # Processed Result
            if aa.stop_processing:
                # Set Stop job status
                break
        self.alarm_log += runner.get_bulk()
        # Only if save-state
        self.alarm.add_watch(
            Effect.ALARM_JOB,
            key=str(self.id),
            after=aa.timestamp,
        )  # Update after_at and key
        self.alarm.safe_save()
        if actions:
            # Split one_time actions/sequenced action
            self.actions = actions + self.actions

    def check_end(self) -> bool:
        return self.leader_item.status == ItemStatus.REMOVED or self.alarm.status == "C"

    @classmethod
    def from_request(
        cls,
        req: AlarmActionRequest,
        alarm: Optional[ActiveAlarm] = None,
        dry_run: bool = False,
        sample: int = 0,
        static_delay: Optional[int] = None,
        stub_tt_system: Optional[TTSystem] = None,
    ) -> "AlarmJob":
        """Create Job from Request"""
        if not alarm and req.item:
            alarm = get_alarm(req.item.alarm)
        if not alarm:
            raise ValueError("Not Found alarm by id: %s", req.item.alarm)
        start = req.start_at or datetime.datetime.now()
        job = AlarmJob(
            # Job Context
            items=[Item.from_alarm(alarm)],
            name=str(req),
            id=req.id,
            actions=[
                ActionLog.from_request(
                    a,
                    started_at=start,
                    user=req.user,
                    tt_system=req.tt_system,
                    stub_tt_system=stub_tt_system,
                )
                for a in req.actions
            ],
            allowed_actions=[AllowedAction.from_request(aa) for aa in req.allowed_actions or []],
            # Settings
            # maintenance_policy=req.maintenance_policy,
            # Repeat settings
            max_repeats=req.max_repeats,
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
        is_clear: bool = False,
        job_id: Optional[str] = None,
        dry_run: bool = False,
        sample: int = 0,
        static_delay: Optional[int] = None,
    ) -> "AlarmJob":
        """
        Restore Job State from Alarm:
        Args:
            alarm: Active alarm Instance
            is_clear: Flag if run from clear_alarm
            job_id: Job State Id
            dry_run: Run from tests (No .save call)
            sample: Telemetry sample
            static_delay: Delay over action (for tests)
        """
        # TTSystem
        job = AlarmJob(
            # Job Context
            # Item.from_alarm
            items=[Item.from_alarm(alarm, is_clear=is_clear)],
            id=ObjectId(),
            actions=ActionLog.from_alarm(alarm, is_clear=is_clear),
            allowed_actions=[
                AllowedAction(action=AlarmAction.ACK),
                AllowedAction(action=AlarmAction.UN_ACK),
            ],
            telemetry_sample=sample,
            dry_run=dry_run,
            static_delay=static_delay,
        )
        return job

    def save_state(self):
        from noc.fm.models.alarmjob import (
            AlarmJob as AlarmJobState,
            AlarmItem,
            ActionLog,
            JobStatus,
        )

        tt_docs, actions = {}, []
        start_at = None
        for a in self.actions:
            if a.action == AlarmAction.CREATE_TT and a.document_id:
                tt_docs[a.key] = a.document_id
            if not start_at and a.status == ActionStatus.NEW:
                start_at = a.timestamp
            actions.append(ActionLog(**a.get_state()))
        job = AlarmJobState(
            name=self.name,
            status=JobStatus.WAITING,
            created_at=self.actions[0].timestamp,
            started_at=start_at,
            ctx_id=self.ctx_id,
            telemetry_sample=self.telemetry_sample,
            maintenance_policy=self.maintenance_policy,
            max_repeats=self.max_repeats,
            repeat_delay=self.repeat_delay,
            items=[AlarmItem(alarm=i.alarm.id, status=i.status) for i in self.items],
            actions=actions,
            tt_docs=tt_docs,
            groups=[],
            # total_objects=self.total_objects,
            # total_services=self.total_services,
            # total_subscribers=self.total_subscribers,
        )
        try:
            job.save()
        except Exception:
            error_report()

    @classmethod
    def from_state(cls, data: Dict[str, Any]) -> Optional["AlarmJob"]:
        """"""
        alarms = {}
        for d in data["items"]:
            alarms[d["alarm"]] = ItemStatus(d["status"])
        items = []
        for aa in ActiveAlarm.objects.filter(id__in=list(alarms)):
            items.append(Item(alarm=aa, status=alarms.pop(aa.id)))
        for alarm_id, status in alarms.items():
            alarm = get_alarm(alarm_id)
            if alarm:
                items.append(Item(alarm=aa, status=ItemStatus.from_alarm(alarm)))
        if not items:
            raise ValueError("Not Found alarm by id: %s", data["items"])
        job = AlarmJob(
            # Job Context
            items=items,
            name=str(data["name"]),
            id=data["_id"],
            actions=[ActionLog.from_state(a) for a in data["actions"]],
            # allowed_actions=[AllowedAction.from_request(aa) for aa in req.allowed_actions],
            # Settings
            maintenance_policy=data["maintenance_policy"],
            # Repeat settings
            max_repeats=data.get("max_repeats", 0),
            repeat_delay=data["repeat_delay"],
            # Span
            ctx_id=data.get("ctx_id"),
            telemetry_sample=data["telemetry_sample"],
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
        timestamp = timestamp or datetime.datetime.now()
        # self.add_action(action, timestamp)
        al = ActionLog.from_request(
            action,
            started_at=timestamp,
            user=user.id if user else None,
            tt_system=str(tt_system.id) if tt_system else None,
            one_time=True,
        )
        self.actions += [al]
        self.run()

    @classmethod
    def ensure_job(cls, tt_id: str) -> Optional["AlarmJob"]:
        """ensure_tt_job"""
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


def touch_alarm(alarm, *args, **kwargs):
    a = ActiveAlarm.objects.filter(id=alarm).first()
    if not a:
        print("[%s] Alarm is not found, skipping", alarm)
        return
    a.touch_watch()
    if a.wait_ts:
        Job.retry_after(delay=(a.wait_ts - datetime.datetime.now()).total_seconds())
