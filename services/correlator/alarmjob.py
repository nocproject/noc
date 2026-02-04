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
from typing import List, Optional, Any, Union, Dict, Iterable, Tuple, Set

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.fm.enum import ActionStatus, AlarmAction, ItemStatus, GroupType
from noc.core.fm.request import AlarmActionRequest, ActionConfig, WhenCondition
from noc.core.models.escalationpolicy import EscalationPolicy
from noc.core.debug import error_report
from noc.core.scheduler.job import Job
from noc.core.scheduler.periodicjob import PeriodicJob
from noc.core.lock.process import ProcessLock
from noc.core.change.policy import change_tracker
from noc.core.span import Span, PARENT_SAMPLE
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.fm.models.alarmwatch import Effect, WatchItem
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm
from .actionlog import ActionLog, ActionResult
from .alarmaction import AlarmActionRunner

WAIT_DEFAULT_INTERVAL_SEC = 120
MIN_NEXT_SHIFT_SEC = 10
ALARM_WATCHER_JCLS = "noc.services.correlator.alarmjob.AlarmWatchersJob"


@dataclass(repr=True)
class Item(object):
    """Over Job Item"""

    #! Replace to alarm List, status
    alarm: Union[ActiveAlarm, ArchivedAlarm]
    # For requested Escalation by ManagedObject
    managed_object_id: Optional[int] = None
    status: ItemStatus = ItemStatus.NEW

    def __str__(self):
        return f"{self.alarm}: {self.status}"

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        return ManagedObject.get_by_id(self.managed_object_id)

    @property
    def is_close(self) -> bool:
        """"""
        return self.status in {ItemStatus.REMOVED, ItemStatus.ARCHIVED}

    def get_state(self):
        return {"alarm": self.alarm.id, "status": self.status.value}

    @classmethod
    def from_alarm(cls, alarm, is_clear: bool = False) -> "Item":
        """Create Item from Alarm"""
        if not alarm:
            return Item(alarm=None, status=ItemStatus.ARCHIVED)
        return Item(
            alarm=alarm,
            managed_object_id=alarm.managed_object.id if alarm.managed_object else None,
            status=ItemStatus.from_alarm(alarm, is_clear=is_clear),
        )


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

    lock = ProcessLock(category="alarmjob", owner="correlator")

    def __init__(
        self,
        items: List[Item],
        actions: List[ActionLog],
        profile: Optional[str] = None,
        allowed_actions: Optional[List[AllowedAction]] = None,
        maintenance_policy: str = None,
        item_policy: EscalationPolicy = EscalationPolicy.ROOT,
        end_condition: str = "CR",
        severity: int = 0,
        # Repeat
        max_repeats: int = 0,
        repeat_delay: int = 60,
        # Span Context
        ctx_id: Optional[int] = None,
        telemetry_sample: Optional[int] = None,
        # Id document
        name: Optional[str] = None,
        job_id: Optional[str] = None,
        # Debug
        logger: Optional[logging.Logger] = None,
        dry_run: bool = False,
        static_delay: Optional[int] = None,
    ):
        self.id = job_id
        self.name = name
        self.profile = profile
        self.items: List[Item] = items
        self.services: List[str] = []
        self.groups: List[bytes] = []
        self.actions = actions
        self.base_severity = severity
        # Policies
        self.maintenance_policy = maintenance_policy or "e"
        self.items_policy = item_policy or EscalationPolicy.ROOT
        self.end_condition = end_condition or "CR"
        # OneTime actions
        self.allowed_actions = allowed_actions
        # Repeat
        self.max_repeats = max_repeats
        self.repeat_delay = repeat_delay
        # Span
        self.ctx_id = ctx_id
        self.telemetry_sample = telemetry_sample
        self.dry_run = dry_run
        self.static_delay: Optional[int] = static_delay
        # Alarm Severity
        self.logger = PrefixLoggerAdapter(
            logger or logging.getLogger(__name__), f"{self.id}|{self.profile}|{self.alarm}"
        )

    def __str__(self):
        # additional
        return f"AlarmJob: {self.alarm}"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def get_by_id(cls, oid) -> Optional["AlarmJob"]:
        from noc.fm.models.alarmjob import AlarmJob as AlarmJobState

        state = AlarmJobState.objects.filter(id=oid).as_pymongo()
        if state:
            return AlarmJob.from_state(state[0])
        return None

    @property
    def leader_item(self) -> "Item":
        """Return first item"""
        if self.items[0].status == ItemStatus.ARCHIVED:
            raise ValueError("Not found Alarm Leader")
        return self.items[0]

    @property
    def alarm(self) -> ActiveAlarm:
        """Getting document alarm"""
        return self.leader_item.alarm

    def get_lock_items(self) -> List[str]:
        """"""
        r = set()
        # Add items
        for item in self.items:
            r.add(f"a:{item.alarm}")
        # Add references
        if self.groups:
            for group in self.groups:
                r.add(f"g:{group}")
        return list(r)

    @property
    def is_end(self) -> bool:
        match self.end_condition:
            case "CR" | "CT":
                return self.leader_item.is_close or self.alarm.status == "C"
            case "CA":
                # Close All
                return all(ii.is_close for ii in self.items)
            case "M":
                # Manual
                return False
        return True

    @property
    def alarm_wait_ended(self) -> bool:
        """Alarm must wait escalation ended before close"""
        return self.end_condition in ("CT", "M")

    @property
    def in_maintenance(self) -> bool:
        """Check Job has active maintenance"""
        if self.maintenance_policy == "i":
            return False
        # If group - check group instance
        # For other - check object instance
        return False

    def has_state(self):
        """Check log for state logs"""
        return any(ll.status != ActionStatus.SKIP for ll in self.actions)

    def get_next_ts(self) -> Optional[datetime.datetime]:
        """
        Calculate next run ts. When set delay or Temp Error
        """
        for aa in sorted(self.actions, key=operator.attrgetter("timestamp")):
            if aa.status == ActionStatus.NEW and aa.when != WhenCondition.ON_END:
                return (aa.timestamp + datetime.timedelta(seconds=1)).replace(microsecond=0)
        return None

    def get_span_sample(self) -> int:
        """
        Calculate effective sample for escalation span
        """
        return PARENT_SAMPLE

    @property
    def severity(self) -> int:
        return self.alarm.severity

    @property
    def is_group(self) -> bool:
        """Group Alarm Escalation"""
        return bool(self.groups)

    @classmethod
    def ensure_profile_job(cls, alarm: ActiveAlarm, profile: str) -> "AlarmJob":
        """Ensure escalation Job"""
        from noc.fm.models.escalationprofile import EscalationProfile
        from noc.fm.models.alarmwatch import Effect

        profile = EscalationProfile.get_by_id(profile)
        if not profile:
            raise ValueError("Not found escalation profile by id")
        job = None
        for w in alarm.watchers:
            if w.effect == Effect.ESCALATION and w.key == str(profile.id) and w.job:
                job = AlarmJob.get_by_id(w.job)
        if job:
            return job
        req = profile.from_alarm(alarm)
        job = AlarmJob.from_request(req, alarm=alarm, profile=str(profile.id))
        alarm.add_watch(Effect.ESCALATION, key=str(profile.id), job=str(job.id))
        alarm.log_message(
            f"Send escalation for profile {profile}. On Job: {req.id}",
            to_save=True,
        )
        return job

    def check_escalated(self):
        """Check Alarm already processed on other job"""
        if not self.is_group:
            # Non-group alarms
            aa = ActiveAlarm.objects.filter(id=self.alarm.id).first()
            if not aa:
                self.items[0].status = ItemStatus.REMOVED
            else:
                # Item Status Exists
                self.items[0] = Item(alarm=aa, status=ItemStatus.from_alarm(aa))
            return
        r = {}
        for aa in ActiveAlarm.objects.filter(groups_in=self.groups):
            r[aa.id] = aa
        for ii in self.items:
            aa = r.get(ii.alarm.id)
            if aa:
                ii.alarm = aa
                ii.status = ItemStatus.from_alarm(aa)

    def sync_items_status(self):
        """Sync items status after Processed, Reset New Elements"""
        new_groups = []
        for ii in self.items[1:]:
            if self.is_group and ii.status == ItemStatus.NEW:
                # Ensure Profile
                new_groups.append(ii.alarm.id)
            if ii.status in {ItemStatus.NEW, ItemStatus.CHANGED}:
                ii.status = ItemStatus.PROCESSED
        # Set Escalation on groups
        if self.profile and new_groups:
            ActiveAlarm.objects.filter(id__in=new_groups).update(
                push__watchers=WatchItem(
                    effect=Effect.ESCALATION, key=str(self.profile), job=str(self.id)
                ),
            )

    def run(
        self,
        ts: Optional[datetime.datetime] = None,
        save_state: bool = True,
        force_end: bool = False,
    ):
        """Main run action for job"""
        now = ts or datetime.datetime.now().replace(microsecond=0)
        if not self.items:
            self.logger.info("Nothing alarms for escalate")
            return
        changed = self.severity != self.base_severity
        is_end = force_end or self.is_end
        self.logger.info(
            "Start actions at: %s (End: %s,Severity: %s, Actions: %s)",
            now,
            is_end,
            changed,
            len(self.actions),
        )
        runner = AlarmActionRunner(
            self.items,
            logger=self.logger,
            allowed_actions=self.allowed_actions,
            services=self.services,
            groups=self.groups,
        )
        # Action Context
        with (
            Span(client="alarmjob", sample=self.get_span_sample()),
            self.lock.acquire(self.get_lock_items()),
            change_tracker.bulk_changes(),
        ):
            self.check_escalated()
            alarm_ctx = self.alarm.get_message_ctx()
            for aa in sorted(self.actions, key=operator.attrgetter("timestamp")):
                self.logger.debug(
                    "[%s] Processed action, with status: %s",
                    aa.action,
                    aa.status,
                )
                if aa.status == ActionStatus.FAILED:
                    continue
                if aa.when != WhenCondition.ON_END and is_end:
                    self.logger.debug("[%s] Action execute on End. Next...", aa.action)
                    continue
                if aa.timestamp > now:
                    self.logger.info("Next action delayed: %s", aa.timestamp - now)
                    break
                # Wait Changed
                if aa.status == ActionStatus.SUCCESS and not changed:
                    # Skip already running job
                    if self.dry_run:
                        self.logger.debug("[%s] Action already executed. Next...", aa)
                    continue
                if not aa.is_match(self.severity, now, self.alarm.ack_user):
                    # Set Skip (Condition)
                    self.logger.debug(
                        "[%s] Action condition [%s] not Match. Next...",
                        aa.action,
                        self.severity,
                    )
                    aa.set_status(ActionResult(status=ActionStatus.SKIP))
                    continue
                if self.dry_run and self.static_delay:
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
                if aa.repeat_num < self.max_repeats and r.status == ActionStatus.SUCCESS:
                    # If Repeat - add action to next on repeat delay
                    # Self register actions, repeat after end actions
                    self.actions.append(aa.get_repeat(self.repeat_delay))
                if r.action:
                    self.actions.append(
                        ActionLog.from_request(
                            r.action,
                            started_at=aa.timestamp,
                            document_id=r.document_id,
                        )
                    )
                if self.end_condition == "CT" and r.document_id and not is_end:
                    self.alarm.add_watch(Effect.STOP_CLEAR, key=str(self.id), immediate=True)
                # AlarmLog
                aa.set_status(r)
                # Processed Result
                if aa.stop_processing:
                    # Set Stop job status
                    break
            if self.alarm.status == "A":
                self.alarm.safe_save()
            # Is_closed
        # Update log and watchers
        self.sync_items_status()
        if save_state:
            # Only if save-state
            self.save_state(is_completed=is_end)

    def get_leader(self) -> Tuple[Optional[ActiveAlarm], List[bytes], Set[ObjectId]]:
        """
        Detect escalation Leader by Escalation Policy
        Group
        """
        if self.alarm.root:
            # Not Root Alarm not escalated, or ALWAYS ?
            return None, [], set()
        if self.alarm.group_type == GroupType.SERVICE and self.alarm.vars.get("service"):
            services = {ObjectId(self.alarm.vars["service"])}
        else:
            services = set(self.alarm.affected_services)
        if (
            self.alarm.group_type in {GroupType.SERVICE, GroupType.GROUP}
            and self.items_policy != EscalationPolicy.ROOT
        ):
            groups = {self.alarm.reference}
        elif self.alarm.groups and self.items_policy in {
            EscalationPolicy.ALWAYS_FIRST,
            EscalationPolicy.ROOT_FIRST,
        }:
            groups = set(self.alarm.groups)
        else:
            groups = set()
        # Apply Policy
        if self.items_policy == EscalationPolicy.ROOT:
            return self.alarm, [], services
        return self.alarm, list(groups), set(services)

    def refresh_items(self, include_groups: bool = False):
        """Build alarm items by Policy"""
        alarms = {ii.alarm.id: ii for ii in self.items[1:]}
        leader, groups, services = self.get_leader()
        if not leader:
            self.items = []
            return
        item = Item.from_alarm(leader)
        if leader.managed_object:
            item.managed_object_id = leader.managed_object.id
        # First as Leader
        items = [item]
        for aa in self.iter_escalation_alarms(leader, groups):
            if aa.affected_services:
                services |= set(aa.affected_services)
            if aa.id == leader.id:
                continue
            item = alarms.pop(aa.id, None)
            # Update Status ?
            if not item:
                # Update status
                item = Item(alarm=aa, status=ItemStatus.from_alarm(aa))
            if aa.managed_object:
                item.managed_object_id = aa.managed_object.id
            items.append(item)
        for ii in alarms.values():
            items.append(Item(alarm=ii.alarm, status=ItemStatus.REMOVED))
        # Refresh Maintenance ?
        self.items = items
        self.services = list(services)
        if include_groups:
            self.groups = groups

    def update_item(self, alarm: ActiveAlarm, is_clear: bool = False):
        """Update job item"""
        for i in self.items:
            if i.alarm.id == alarm.id:
                i.status = ItemStatus.from_alarm(alarm, is_clear)
                i.alarm = alarm

    @classmethod
    def from_request(
        cls,
        req: AlarmActionRequest,
        alarm: Optional[ActiveAlarm] = None,
        profile: Optional[str] = None,
        dry_run: bool = False,
        sample: int = 0,
        static_delay: Optional[int] = None,
        stub_tt_system: Optional[TTSystem] = None,
        stub_user: Optional[User] = None,
    ) -> "AlarmJob":
        """Create Job from Request"""
        if not alarm and req.item:
            alarm = get_alarm(req.item.alarm)
        if not alarm:
            raise ValueError("Not Found alarm by id: %s", req.item.alarm)
        start = req.start_at or datetime.datetime.now()
        return AlarmJob(
            # Job Context
            items=[Item.from_alarm(alarm)],
            name=str(req.name),
            profile=profile,
            job_id=req.id,
            actions=[
                ActionLog.from_request(
                    a,
                    started_at=start,
                    user=req.user or stub_user,
                    tt_system=req.tt_system,
                    stub_tt_system=stub_tt_system,
                )
                for a in req.actions
            ],
            allowed_actions=[AllowedAction.from_request(aa) for aa in req.allowed_actions or []],
            # Settings
            # maintenance_policy=req.maintenance_policy,
            end_condition=req.end_condition,
            item_policy=req.item_policy,
            # Repeat settings
            max_repeats=req.max_repeats,
            repeat_delay=req.repeat_delay,
            # Span
            ctx_id=req.ctx,
            telemetry_sample=sample,
            dry_run=dry_run,
            static_delay=static_delay,
        )

    @classmethod
    def from_alarm(
        cls,
        alarm: ActiveAlarm,
        is_clear: bool = False,
        dry_run: bool = False,
        sample: int = 0,
        static_delay: Optional[int] = None,
    ) -> "AlarmJob":
        """
        Restore Job State from Alarm:
        Args:
            alarm: Active alarm Instance
            is_clear: Flag if run from clear_alarm
            dry_run: Run from tests (No .save call)
            sample: Telemetry sample
            static_delay: Delay over action (for tests)
        """
        # TTSystem
        return AlarmJob(
            # Job Context
            # Item.from_alarm
            items=[Item.from_alarm(alarm, is_clear=is_clear)],
            job_id=ObjectId(),
            actions=ActionLog.from_alarm(alarm, is_clear=is_clear),
            allowed_actions=[
                AllowedAction(action=AlarmAction.ACK),
                AllowedAction(action=AlarmAction.UN_ACK),
            ],
            telemetry_sample=sample,
            dry_run=dry_run,
            static_delay=static_delay,
        )

    def save_state(self, dry_run: bool = False, is_completed: bool = False):
        from noc.fm.models.alarmjob import (
            AlarmJob as AlarmJobState,
            AlarmItem,
            ActionLog,
            JobStatus,
        )

        tt_docs, actions = {}, []
        start_at, completed_at = None, None
        status = JobStatus.WAITING
        if is_completed:
            completed_at = datetime.datetime.now().replace(microsecond=0)
            status = JobStatus.SUCCESS
        for a in self.actions:
            if a.action == AlarmAction.CREATE_TT and a.document_id:
                tt_docs[a.key] = a.document_id
            if not start_at and a.status == ActionStatus.NEW:
                start_at = a.timestamp
            actions.append(ActionLog(**a.get_state()))
        state = AlarmJobState(
            id=self.id,
            name=self.name,
            escalation_profile=self.profile,
            status=status,
            created_at=actions[0].timestamp,
            started_at=start_at,
            completed_at=completed_at,
            ctx_id=self.ctx_id,
            telemetry_sample=self.telemetry_sample,
            maintenance_policy=self.maintenance_policy,
            end_condition=self.end_condition,
            max_repeats=self.max_repeats,
            repeat_delay=self.repeat_delay,
            is_dirty=False,
            items=[AlarmItem(alarm=i.alarm.id, status=i.status) for i in self.items],
            actions=actions,
            tt_docs=tt_docs,
            groups=self.groups,
            affected_services=self.services,
            severity=self.severity,
            # total_objects=self.total_objects,
            # total_services=self.total_services,
            # total_subscribers=self.total_subscribers,
        )
        if dry_run:
            return state
        try:
            state.save()
        except Exception:
            error_report()

    @classmethod
    def items_from_state(cls, items: List[Dict[str, Any]]) -> List[Item]:
        """Build items from state"""
        r = []
        items = {x["alarm"]: x["status"] for x in items}
        for aa in ActiveAlarm.objects.filter(id__in=list(items)):
            status = items.pop(aa.id, None)
            if not status:
                continue
            r.append(Item(alarm=aa, status=ItemStatus(status)))
        if not items:
            return r
        for aa in ArchivedAlarm.objects.filter(id__in=list(items)):
            ii = items.pop(aa.id, None)
            if not ii:
                continue
            r.append(Item.from_alarm(alarm=aa))
        for _ in items:
            r.append(Item(alarm=None, status=ItemStatus.REMOVED))
        return r

    def iter_escalation_alarms(
        self, alarm: ActiveAlarm, groups: List[bytes]
    ) -> Iterable[ActiveAlarm]:
        """Iter over alarms on items"""
        if groups:
            yield from self.iter_groups_alarm(groups)
        if not alarm.root:
            yield from self.iter_consequence(alarm)

    def iter_consequence(self, alarm: ActiveAlarm):
        """Iter Alarm consequence"""
        if alarm.root:
            return
        if self.items_policy == EscalationPolicy.ROOT:
            yield alarm
        yield from alarm.iter_consequences()

    def iter_groups_alarm(self, groups: List[bytes]):
        """Iterate over groups alarm"""
        if self.items_policy not in {EscalationPolicy.ROOT_FIRST, EscalationPolicy.ALWAYS_FIRST}:
            return
        for aa in ActiveAlarm.objects.filter(groups__in=groups).order_by("root", "-timestamp"):
            yield aa
        for aa in ActiveAlarm.objects.filter(reference__in=groups):
            yield aa

    @classmethod
    def from_state(
        cls, data: Dict[str, Any], stub_alarms: Optional[List[ActiveAlarm]] = None
    ) -> Optional["AlarmJob"]:
        """"""
        if stub_alarms:
            items = [Item.from_alarm(a) for a in stub_alarms]
        else:
            items = AlarmJob.items_from_state(data["items"])
        if not items:
            raise ValueError("Not Found alarm by id: %s", data["items"])
        job = AlarmJob(
            # Job Context
            items=items,
            name=str(data["name"]),
            profile=data.get("escalation_profile"),
            job_id=data["_id"],
            actions=[ActionLog.from_state(a) for a in data["actions"]],
            severity=data.get("severity", 0),
            # allowed_actions=[AllowedAction.from_request(aa) for aa in req.allowed_actions],
            # Settings
            maintenance_policy=data["maintenance_policy"],
            end_condition=data.get("end_condition", "CR"),
            # Repeat settings
            max_repeats=data.get("max_repeats", 0),
            repeat_delay=data["repeat_delay"],
            # Span
            ctx_id=data.get("ctx_id"),
            telemetry_sample=data["telemetry_sample"],
        )
        if data.get("is_dirty"):
            # On first Run
            job.refresh_items(include_groups=True)
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
            started_at=timestamp.replace(microsecond=0),
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
            return None
        return AlarmJob.from_alarm(aa)

    @classmethod
    def get_by_tt_id(cls, tt_id) -> Optional["AlarmJob"]:
        """Getting Alarm Job by TT ID"""
        return None


class AlarmWatchersJob(PeriodicJob):
    def handler(self, **kwargs):
        now = datetime.datetime.now().replace(microsecond=0)
        for aa in ActiveAlarm.objects.filter(wait_ts__lte=now):
            aa.touch_watch()
            aa.wait_ts = aa.get_wait_ts()
            aa.safe_save()
            # Clean After
            # Bulk ?

    def can_run(self):
        return True

    def get_next_timestamp(self, interval, offset=0.0, ts=None):
        """
        Returns next repeat interval
        """
        now = datetime.datetime.now().replace(microsecond=0)
        next_ts = ActiveAlarm.get_min_wait_ts()
        if not next_ts:
            next_ts = now + datetime.timedelta(seconds=WAIT_DEFAULT_INTERVAL_SEC)
        elif next_ts <= now:
            next_ts = now + datetime.timedelta(seconds=MIN_NEXT_SHIFT_SEC)
        self.logger.info("Schedule next ActiveAlarm watcher: %s", next_ts)
        return next_ts


def run_alarm_job(job_id: str, *args, **kwargs):
    job = AlarmJob.get_by_id(job_id)
    if not job:
        print("Unknown job")
        return
    job.run()
    wait_ts = job.get_next_ts()
    if wait_ts:
        Job.retry_after(delay=(wait_ts - datetime.datetime.now()).total_seconds())


def touch_alarm(alarm, *args, **kwargs):
    a = ActiveAlarm.objects.filter(id=alarm).first()
    if not a:
        print(f"[{alarm}] Alarm is not found, skipping")
        return
    a.touch_watch()
    if a.wait_ts:
        print(a.watchers, a.wait_ts)
        Job.retry_after(delay=(a.wait_ts - datetime.datetime.now()).total_seconds())
