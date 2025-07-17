# ----------------------------------------------------------------------
# Escalation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import operator
import threading
from typing import Iterable, Dict, DefaultDict, List, Optional, Any, NoReturn
from collections import defaultdict
from abc import ABC, abstractmethod

# Third-party modules
from bson import ObjectId

# NOC modules
from noc.fm.models.utils import get_alarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.alarmescalation import AlarmEscalation, EscalationItem as AEscalationItem
from noc.sa.models.serviceprofile import ServiceProfile
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.maintenance.models.maintenance import Maintenance
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.archivedalarm import ArchivedAlarm
from noc.core.perf import metrics
from noc.main.models.notificationgroup import NotificationGroup
from noc.config import config
from noc.core.scheduler.job import Job
from noc.core.span import Span, PARENT_SAMPLE
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.change.policy import change_tracker
from noc.fm.models.escalation import Escalation, EscalationItem
from noc.core.models.escalationpolicy import EscalationPolicy
from noc.core.lock.process import ProcessLock
from noc.core.log import PrefixLoggerAdapter
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.core.defer import call_later
from noc.core.tt.types import EscalationItem as ECtxItem, EscalationStatus
from noc.core.tt.base import TTSystemCtx


logger = logging.getLogger(__name__)

RETRY_TIMEOUT = config.escalator.retry_timeout
# @fixme have to be checked
RETRY_DELTA = 60 / max(config.escalator.tt_escalation_limit - 1, 1)
ESCALATION_CHECk_CLOSE_DELAY = 30

retry_lock = threading.Lock()
next_retry = datetime.datetime.now()


class BaseSequence(ABC):
    """
    Base class for escalation/deescalation sequence
    """

    lock = ProcessLock(category="escalator", owner="escalator")

    class StopSequence(Exception):
        pass

    def __init__(self, alarm_id: str, login: str = "correlator") -> None:
        self.logger = PrefixLoggerAdapter(logger, str(alarm_id))
        self.login: str = login

    def retry_job(self, msg: str, delay: int = None) -> NoReturn:
        """
        Reschedule current job and stop escalation
        :param msg: Retry
        :param delay: In seconds
        """
        global RETRY_DELTA, RETRY_TIMEOUT, next_retry, retry_lock

        if delay:
            Job.retry_after(delay + 60, msg)
            return
        now = datetime.datetime.now()
        retry = now + datetime.timedelta(seconds=RETRY_TIMEOUT)
        with retry_lock:
            if retry < next_retry:
                retry = next_retry
            next_retry = retry + datetime.timedelta(seconds=RETRY_DELTA)
        delta = retry - now
        delay = delta.seconds + (1 if delta.microseconds else 0)
        Job.retry_after(delay, msg)

    def stop_sequence(self) -> NoReturn:
        """
        Stop sequence
        """
        raise self.StopSequence

    def run(self) -> None:
        """
        Start and process sequence
        """
        try:
            self.process()
        except self.StopSequence:
            pass

    @abstractmethod
    def process(self) -> None:
        """
        Base logic
        """


class EscalationSequence(BaseSequence):
    """
    Process all escalation procedures
    """

    def __init__(
        self,
        alarm_id: str,
        escalation_id: str,
        escalation_delay: int,
        login: str = "correlator",
        timestamp_policy: str = "a",
        force: bool = False,
        prev_escalation: Optional[str] = None,
    ):
        super().__init__(alarm_id=alarm_id, login=login)
        self.alarm = self.get_alarm(alarm_id)
        self.prev_escalation = ObjectId(prev_escalation) if prev_escalation else None
        self.escalation = self.get_escalation(escalation_id)
        self.escalation_delay = escalation_delay
        self.timestamp_policy = timestamp_policy
        self.force = force
        self.alarm_ids: Dict[ObjectId, ActiveAlarm] = {}
        self.escalation_doc: Escalation

    def log_alarm(self, message: str, *args) -> None:
        """
        Log message to alarm
        """
        msg = message % args
        self.logger.info(msg)
        self.alarm.log_message(msg, to_save=True)

    def get_alarm(self, alarm_id: str) -> ActiveAlarm:
        """
        Get active alarm by id. Raise StopSequence if
        alarm is not found or already closed.
        """
        alarm = get_alarm(alarm_id)
        if alarm is None:
            self.logger.info("Missing alarm, skipping")
            metrics["escalation_missed_alarm"] += 1
            self.stop_sequence()
        if alarm.status == "C":
            logger.info("Alarm is closed, skipping")
            metrics["escalation_already_closed"] += 1
            self.stop_sequence()
        return alarm

    def get_escalation(self, escalation_id: str) -> AlarmEscalation:
        """
        Get alarm escalation by id. Raise StopSequence if not found.
        """
        escalation = AlarmEscalation.get_by_id(escalation_id)
        if not escalation:
            self.log_alarm(f"Escalation {escalation_id} is not found, skipping")
            metrics["escalation_not_found"] += 1
            self.stop_sequence()
        return escalation

    def get_span_sample(self) -> int:
        """
        Calculate effective sample for escalation span
        """
        if self.alarm.managed_object.tt_system:
            return self.alarm.managed_object.tt_system.telemetry_sample
        return PARENT_SAMPLE

    def iter_escalation_items(self) -> Iterable[AEscalationItem]:
        """
        Iterate all applicable EscalationItems
        """
        for item in self.escalation.escalations:
            if item.delay != self.escalation_delay:
                continue  # Try other type
            # Check administrative domain
            if (
                item.administrative_domain
                and item.administrative_domain.id not in self.alarm.adm_path
            ):
                continue
            # Check severity
            if item.min_severity and self.alarm.severity < item.min_severity:
                continue
            # Check resource group
            if (
                item.resource_group
                and str(item.resource_group.id)
                not in self.alarm.managed_object.effective_service_groups
            ):
                continue
            # Check time pattern
            if item.time_pattern and not item.time_pattern.match(self.alarm.timestamp):
                continue
            # Render escalation message
            if not item.template:
                self.log_alarm("No escalation template, skipping")
                continue
            yield item

    def check_throttling(self) -> None:
        """
        Check throttling limits. Retry job if overwhelmed.
        """
        limit = config.escalator.tt_escalation_limit
        widow = datetime.datetime.now() - datetime.timedelta(seconds=config.escalator.ets)
        n_escalated = ActiveAlarm._get_collection().count_documents(
            {"escalation_ts": {"$gte": widow}}
        )
        n_escalated += ArchivedAlarm._get_collection().count_documents(
            {"escalation_ts": {"$gte": widow}}
        )
        if n_escalated < limit:
            return
        self.logger.error(
            "Escalation limit exceeded (%s/%s). Skipping",
            n_escalated,
            config.escalator.tt_escalation_limit,
        )
        metrics["escalation_throttled"] += 1
        self.retry_job(f"Escalation limit exceeded ({n_escalated}/{limit}). Skipping")

    def can_escalate(self) -> bool:
        """
        Return True if alarm can be escalated.
        """
        if self.force:
            return True
        return self.alarm.managed_object.can_escalate()

    def can_notify(self) -> bool:
        """
        Return True if alarm can send notifications
        """
        if self.force:
            return True
        return self.alarm.managed_object.can_notify()

    def get_timestamp(self) -> Optional[datetime.datetime]:
        """
        Get effective timestamp according to timestamp policy
        """
        if self.timestamp_policy == "a":
            return self.alarm.timestamp
        return None

    @staticmethod
    def summary_to_list(summary, model):
        r = []
        for k in summary:
            p = model.get_by_id(k.profile)
            if not p or getattr(p, "show_in_summary", True) is False:
                continue
            r += [
                {
                    "profile": p.name,
                    "summary": k.summary,
                    "order": (getattr(p, "display_order", 100), -k.summary),
                }
            ]
        return sorted(r, key=operator.itemgetter("order"))

    def check_closed(self, close_tt: bool = False) -> None:
        """
        Check if alarm has been closed during escalation. Try to deescalate
        """
        tt_id = self.escalation_doc.tt_id
        if not tt_id:
            return
        alarm = get_alarm(self.alarm.id)
        if alarm and alarm.status == "C":
            alarm.log_message("Alarm has been closed during escalation. Try to deescalate")
            self.logger.info("Alarm has been closed during escalation. Try to deescalate")
            metrics["escalation_closed_while_escalated"] += 1
            if tt_id and not alarm.escalation_tt:
                alarm.escalation_ts = datetime.datetime.now()
                alarm.escalation_tt = tt_id
                alarm.save()
            if not alarm.escalation_close_ts and not alarm.escalation_close_error:
                self.escalation_doc.save()  # Will be fetched later
                notify_close(
                    alarm_id=self.alarm.id,
                    tt_id=alarm.escalation_tt,
                    subject="Closing",
                    body="Closing",
                    # notification_group_id=(
                    #     self.alarm.clear_notification_group.id
                    #     if self.alarm.clear_notification_group
                    #     else None
                    # ),
                    close_tt=close_tt,
                    login=self.login,
                    queue=self.alarm.managed_object.tt_queue,
                )
            return
        if alarm == "A" and not alarm.escalation_tt and tt_id:
            self.logger.error("[%s] Alarm without escalation TT: %s", alarm.id, tt_id)

    def has_merged_downlinks(self):
        """
        Check if alarm has merged downlinks
        """
        return bool(
            ActiveAlarm.objects.filter(root=self.alarm.id, rca_type=RCA_DOWNLINK_MERGE).first()
        )

    def has_unavailable_alarm(self) -> bool:
        """
        Return true if alarm is unavailable service
        :return:
        """
        return self.alarm.alarm_class.name == "NOC | Managed Object | Ping Failed"

    # TT System API
    def get_tt_system_context(
        self,
        tt_system: TTSystem,
        tt_id: Optional[str] = None,
        queue: Optional[str] = None,
        pre_reason: Optional[str] = None,
    ) -> TTSystemCtx:
        ctx = TTSystemCtx(
            id=tt_id,
            tt_system=tt_system.get_system(),
            queue=queue,
            reason=pre_reason,
            login=self.login,
            timestamp=self.get_timestamp(),
            is_unavailable=self.has_unavailable_alarm(),
        )
        return ctx

    def get_ctx(self):
        """
        Get escalation context
        """
        affected_objects = sorted(self.alarm.iter_affected(), key=operator.attrgetter("name"))
        segment = self.alarm.managed_object.segment
        if segment.is_redundant:
            uplinks = self.alarm.managed_object.uplinks
            lost_redundancy = len(uplinks) > 1
            affected_subscribers = self.summary_to_list(
                segment.total_subscribers, SubscriberProfile
            )
            affected_services = self.summary_to_list(segment.total_services, ServiceProfile)
        else:
            lost_redundancy = False
            affected_subscribers = []
            affected_services = []
        cons_escalated = [
            self.alarm_ids[x.alarm]
            for x in self.escalation_doc.consequences
            if x.is_already_escalated
        ]
        return {
            "alarm": self.alarm,
            "affected_objects": affected_objects,
            "cons_escalated": cons_escalated,
            "total_objects": self.summary_to_list(self.alarm.total_objects, ManagedObjectProfile),
            "total_subscribers": self.summary_to_list(
                self.alarm.total_subscribers, SubscriberProfile
            ),
            "total_services": self.summary_to_list(self.alarm.total_services, ServiceProfile),
            "tt": None,
            "lost_redundancy": lost_redundancy,
            "affected_subscribers": affected_subscribers,
            "affected_services": affected_services,
            "has_merged_downlinks": self.has_merged_downlinks(),
        }

    def notify(self, item: AEscalationItem, ctx: Dict[str, Any]) -> bool:
        if not item.notification_group or not self.can_notify():
            return False
        subject = item.template.render_subject(**ctx)
        body = item.template.render_body(**ctx)
        self.logger.debug("Notification message:\nSubject: %s\n%s", subject, body)
        self.log_alarm(f"Sending notification to group {item.notification_group.name}")
        item.notification_group.notify(subject, body)
        self.alarm.set_clear_notification(item.notification_group, item.clear_template)
        metrics["escalation_notify"] += 1
        return True

    def is_under_maintenance(self) -> bool:
        """
        Check if current alarm is covered by existing maintenance.
        Add maintenance details to alarm log when necessary.

        :returns: True if object is under maintenance, False otherwise
        """
        if not self.escalation_doc.leader.is_maintenance:
            return False
        metrics["escalation_stop_on_maintenance"] += 1
        return True

    def is_already_escalated(self) -> bool:
        """
        Check if alarm is already escalated.
        Add escalation details to alarm log when necessary.

        :returns: True if alarm is already escalated, False otherwise
        """
        if (
            not self.escalation_doc.leader.is_already_escalated
            or not self.escalation_doc.leader.current_tt_id
        ):
            # not self.escalation_doc.leader.current_tt_id if notification doc
            return False
        tt = self.escalation_doc.leader.current_tt_id
        self.log_alarm(f"Already escalated with TT #{tt}")
        return True

    def create_tt(self, esc_item: AEscalationItem, ctx: Dict[str, Any]):
        """
        Create trouble ticket for alarm
        """
        mo = self.alarm.managed_object
        pre_reason = self.escalation.get_pre_reason(mo.tt_system)
        if pre_reason is None:
            self.log_alarm("Cannot find pre reason")
            metrics["escalation_tt_fail"] += 1
            return None
        # Build escalation context
        e_ctx_items = [ECtxItem(id=str(mo.id), tt_id=mo.tt_system_id)]
        items_map = {str(mo.id): self.escalation_doc.items[0]}
        for item in self.escalation_doc.items[1:]:
            # @todo: Check escalation status for already escalated and maintenance?
            alarm = self.alarm_ids[item.alarm]
            if not alarm.managed_object.can_escalate(True):
                err = f"Cannot append object {alarm.managed_object.name} to group tt: Escalations are disabled"
                self.log_alarm(err)
                item.escalation_status = "fail"
                item.escalation_error = err
                continue
            if alarm.managed_object.tt_system != mo.tt_system:
                err = f"Cannot append object {alarm.managed_object.name} to group tt: Belongs to other TT system"
                self.log_alarm(err)
                item.escalation_status = "fail"
                item.escalation_error = err
                continue
            ei = ECtxItem(id=str(alarm.managed_object.id), tt_id=alarm.managed_object.tt_system_id)
            e_ctx_items.append(ei)
            items_map[str(alarm.managed_object.id)] = item
        # Render TT subject and body
        #
        subject = esc_item.template.render_subject(**ctx)
        body = esc_item.template.render_body(**ctx)
        self.logger.debug("Escalation message:\nSubject: %s\n%s", subject, body)
        self.log_alarm(f"Creating TT in system {mo.tt_system.name}")
        # tts = mo.tt_system.get_system()
        with self.get_tt_system_context(
            mo.tt_system, queue=mo.tt_queue, pre_reason=pre_reason
        ) as ctx:
            ctx.add_items(e_ctx_items)
            ctx.create(subject=subject, body=body)
        r = ctx.get_result()
        if r.status == EscalationStatus.TEMP:
            metrics["escalation_tt_retry"] += 1
            self.log_alarm(f"Temporary error detected. Retry after {RETRY_TIMEOUT}s")
            mo.tt_system.register_failure()
            self.retry_job(str(r.error))
        elif r.status != EscalationStatus.OK:
            self.log_alarm(f"Failed to create TT: {r.error}")
            metrics["escalation_tt_fail"] += 1
            self.alarm.log_message(f"Failed to escalate: {r.error}", to_save=True)
            return None
        tt = f"{mo.tt_system.name}:{r.document}"
        self.alarm.escalate(
            tt,
            close_tt=esc_item.close_tt,
            wait_tt=tt if esc_item.wait_tt else None,
            template=esc_item.clear_template,
            open_template=esc_item.template
        )
        # Save to escalation context
        self.escalation_doc.tt_id = tt
        self.escalation_doc.leader.escalation_status = "ok"
        # Project result to escalation items
        for item in ctx.items:
            ei = items_map[str(item.id)]
            try:
                e_status = item.get_status()
            except AttributeError:
                self.log_alarm(f"Adapter malfunction. Status for {item.id} is not set.")
                continue
            if e_status == EscalationStatus.OK:
                self.log_alarm(f"{item.id} is appended successfully")
            else:
                self.log_alarm(f"Failed to append {item.id}: {e_status} ({item._message})")
            ei.escalation_status = e_status.value
            # if e_status:
            #    ei.escalation_error = e_status.msg
        metrics["escalation_tt_create"] += 1

    def notify_escalated_consequences(self) -> None:
        """
        Append comments to all escalated consequences
        """
        if not self.escalation_doc.tt_id:
            return
        mo = self.alarm.managed_object
        # Notify consequences
        for item in self.escalation_doc.consequences:
            if not item.is_already_escalated:
                continue
            alarm = self.alarm_ids[item.alarm]
            if not alarm.escalation_tt:
                # Already appended on top tt
                continue
            tt_name, c_tt_id = alarm.escalation_tt.split(":")
            cts = TTSystem.get_by_name(tt_name)
            if not cts:
                self.log_alarm(f"Failed to add comment to {alarm.escalation_tt}: Invalid TT system")
                metrics["escalation_tt_comment_fail"] += 1
                continue
            self.log_alarm(f"Appending comment to TT {self.escalation_doc.tt_id}")
            with self.get_tt_system_context(cts, c_tt_id, queue=mo.tt_queue) as ctx:
                ctx.comment(f"Covered by TT {self.escalation_doc.tt_id}")
            r = ctx.get_result()
            if r.status == EscalationStatus.SKIP:
                self.log_alarm(
                    f"Cannot add comment to {alarm.escalation_tt}: Feature not implemented"
                )
                metrics["escalation_tt_comment_fail"] += 1
            elif r.status != EscalationStatus.OK:
                metrics["escalation_tt_comment_fail"] += 1
                self.log_alarm(f"Failed to add comment to {alarm.escalation_tt}: {r.error}")

    def get_escalation_policy(self) -> EscalationPolicy:
        """
        Get effective escalation policy for alarm
        """
        labels: List[List[str]] = [self.alarm.effective_labels]
        if self.alarm.groups:
            # All groups
            for doc in ActiveAlarm._get_collection().find(
                {"reference": {"$in": self.alarm.groups}}, {"_id": 1, "effective_labels": 1}
            ):
                g_labels = doc.get("effective_labels") or []
                if g_labels:
                    labels.append(g_labels)
        return EscalationPolicy.get_effective_policy(labels)

    def get_escalation_doc(self) -> Optional[Escalation]:
        """
        Get escalation document structure filled with filled EscalationItems
        """

        def update_totals_from_summary(
            t_dict: DefaultDict[ObjectId, int], t_items: Iterable[SummaryItem]
        ) -> None:
            """
            Update totals from alarm summary
            """
            for item in t_items:
                t_dict[item.profile] += item.summary

        policy = self.get_escalation_policy().name.lower()
        iter_items = getattr(self, f"iter_alarms_{policy}", None)
        if not iter_items:
            self.logger.error("Unknown escalation policy `%s`. Skipping", policy)
            return None
        items = list(iter_items())
        if not items:
            return None
        # Total counters
        total_objects: DefaultDict[int, int] = defaultdict(int)
        total_services: DefaultDict[ObjectId, int] = defaultdict(int)
        total_subscribers: DefaultDict[ObjectId, int] = defaultdict(int)
        # @todo: Append profile
        doc = Escalation(
            timestamp=datetime.datetime.now(), items=[], prev_escalation=self.prev_escalation
        )
        for alarm in items:
            if alarm.alarm_class.is_ephemeral:
                # Group alarms are virtual and should be locked, but not escalated
                doc.groups += [str(alarm.reference)]
                continue
            doc.items += [
                EscalationItem(
                    managed_object=alarm.managed_object,
                    alarm=alarm.id,
                )
            ]
            self.alarm_ids[alarm.id] = alarm
            # Update totals
            total_objects[alarm.managed_object.object_profile.id] += 1
            update_totals_from_summary(total_services, alarm.direct_services)
            update_totals_from_summary(total_subscribers, alarm.direct_subscribers)

        if not doc.items:
            return None  # Only group alarms
        doc.total_objects = [
            ObjectSummaryItem(profile=k, summary=v) for k, v in total_objects.items()
        ]
        doc.total_services = [SummaryItem(profile=k, summary=v) for k, v in total_services.items()]
        doc.total_subscribers = [
            SummaryItem(profile=k, summary=v) for k, v in total_subscribers.items()
        ]
        return doc

    def iter_alarms_never(self) -> Iterable[ActiveAlarm]:
        """
        `never` escalationn policy. Yields not items
        """
        self.logger.info("Escalation is denied by policy")
        yield from []

    def iter_alarms_root(self) -> Iterable[ActiveAlarm]:
        """
        `root` escalation policy. If alarm is root cause, yield root alarm
        and all the consequences
        """
        if self.alarm.root:
            logger.info("[root] Alarm is not a root cause. Skipping")
            return
        yield self.alarm
        yield from self.alarm.iter_consequences()

    def iter_alarms_always(self) -> Iterable[ActiveAlarm]:
        """
        `always` escalation policy. Always escalate current alarm
        """
        yield self.alarm

    def iter_alarms_root_first(self) -> Iterable[ActiveAlarm]:
        """
        `root_first` escalation policy. Always escalate current alarm
        """
        if self.alarm.root:
            logger.info("[rootfirst] Alarm is not a root cause. Skipping")
            return
        # Check if any of groups already has any escalated root cause
        if not self.alarm.groups:
            yield from self.iter_alarms_root()
            return
        for aa in ActiveAlarm.objects.filter(groups__in=self.alarm.groups).order_by(
            "root", "-timestamp"
        ):
            if aa.managed_object.can_escalate():
                # Skip Disabled Escalation
                yield aa
                break
        yield from self.alarm.iter_grouped()

    def iter_alarms_always_first(self) -> Iterable[ActiveAlarm]:
        """
        `always_first` escalation policy. Always escalate first alarm
        """
        if not self.alarm.groups:
            yield from self.iter_alarms_always()
            return
        for aa in ActiveAlarm.objects.filter(groups__in=self.alarm.groups).order_by("timestamp"):
            if aa.managed_object.can_escalate():
                # Skip Disabled Escalation
                yield aa
                break
        yield from self.alarm.iter_grouped()

    def check_escalated(self):
        """
        Process escalation doc and fill already escalated alarms.
        Note: Must be called under the lock
        """
        alarms = [item.alarm for item in self.escalation_doc.items]
        esc_status: Dict[ObjectId, ObjectId] = {}
        esc_tt: Dict[ObjectId, str] = {}
        for doc in Escalation._get_collection().aggregate(
            [
                {
                    "$match": {
                        "close_timestamp": {"$exists": False},
                        "items.alarm": {"$in": alarms},
                        "tt_id": {"$exists": True},
                    }
                },
                {"$project": {"_id": 1, "items": 1, "tt_id": 1}},
                {"$unwind": "$items"},
                {"$match": {"items.alarm": {"$in": alarms}}},
            ]
        ):
            esc_status[doc["items"]["alarm"]] = doc["_id"]
            esc_tt[doc["items"]["alarm"]] = doc.get("tt_id", doc["items"].get("current_tt_id"))
        if not esc_status:
            return  # No escalated docs
        for item in self.escalation_doc.items:
            if item.alarm in esc_status and item.is_new:
                self.logger.info(
                    "Alarm %s is already escalated with TT %s", item.alarm, esc_tt[item.alarm]
                )
                item.escalation_status = "exists"
                item.current_escalation = esc_status[item.alarm]
                item.current_tt_id = esc_tt[item.alarm]

    def check_maintenance(self):
        """
        Process escalation doc and mark alarms covered by maintenance.
        Note: Must be called under the lock
        """
        # @todo: Check maintenance for all consequences
        if not self.escalation_doc.leader.is_new:
            return
        mnt_ids = self.alarm.managed_object.get_active_maintenances()
        if not mnt_ids:
            return
        for m_id in mnt_ids:
            maintenance = Maintenance.get_by_id(m_id)
            if maintenance.escalation_policy == "E":
                self.logger.info("Escalation allowed by maintenance policy")
                return
            elif maintenance.escalation_policy == "S":
                delay: datetime.timedelta = maintenance.stop - self.escalation_doc.timestamp
                self.logger.info("Escalation suspended, retry after Maintenance")
                self.log_alarm(f"Escalation suspended. Object is under maintenance: {m_id}")
                self.retry_job("Escalation suspended, retry after Maintenance", delay.seconds)
                continue
            else:
                self.log_alarm(f"Object is under maintenance: {m_id}")
        self.escalation_doc.leader.escalation_status = "maintenance"

    def process(self) -> None:
        """
        Escalation logic. Raising StopSequence forces premature stop.
        """
        self.logger.info("Performing escalations")
        # Get items to escalate
        e_doc = self.get_escalation_doc()
        if not e_doc:
            self.logger.info("Nothing to escalate. Skipping")
            return
        self.escalation_doc = e_doc
        # Check maintenance out-of-the-lock
        self.check_maintenance()
        close_tt = False
        # Perform escalations
        with (
            Span(client="escalator", sample=self.get_span_sample()) as ctx,
            self.lock.acquire(self.escalation_doc.get_lock_items()),
            change_tracker.bulk_changes(),
        ):
            self.check_escalated()
            self.alarm.set_escalation_context()
            # Evaluate escalation chain
            notify = False  # @todo save to escalation doc
            for esc_item in self.iter_escalation_items():
                # Check global limits
                # @todo: Move into escalator service
                # @todo: Process per-ttsystem limits
                self.check_throttling()
                # Render escalation context
                ctx = self.get_ctx()
                # Escalate to TT
                if (
                    esc_item.create_tt
                    and self.can_escalate()
                    and not self.is_already_escalated()
                    and not self.is_under_maintenance()
                ):
                    self.create_tt(esc_item, ctx)
                    self.notify_escalated_consequences()
                    close_tt |= esc_item.close_tt
                # Send notification
                if not self.is_under_maintenance():
                    notify = notify or self.notify(esc_item, ctx)
                if esc_item.stop_processing:
                    logger.debug("Stopping processing")
                    break
            if self.escalation_doc.tt_id or notify:
                self.escalation_doc.save()
        # Check if alarm has been closed during escalation
        self.check_closed(close_tt)
        # Escalation process complete
        self.logger.info("Escalation sequence is completed")


class DeescalationSequence(BaseSequence):
    def __init__(
        self,
        alarm_id: str,
        tt_id: str,
        subject: str,
        body: str,
        notification_group_id: Optional[str] = None,
        close_tt: bool = False,
        login: str = "corellator",
        queue: Optional[str] = None,
    ) -> None:
        super().__init__(alarm_id=alarm_id, login=login)
        self.alarm = self.get_alarm(alarm_id)
        self.escalation_doc = self.get_escalation_doc()
        self.notification_group = self.get_notification_group(notification_group_id)
        self.tts = self.get_tts(tt_id)
        self.tt_id = tt_id
        self.to_close_tt = close_tt
        self.subject = subject
        self.body = body
        self.queue = queue

    def log_alarm(self, message: str, *args) -> None:
        """
        Log message to alarm
        """
        msg = message % args
        self.logger.info(msg)
        self.alarm.log_message(msg)

    def get_alarm(self, alarm_id: str) -> ArchivedAlarm:
        """
        Get active alarm by id. Raise StopSequence if
        alarm is not found or not closed.
        """
        alarm = get_alarm(alarm_id)
        if alarm is None:
            self.logger.info("Missing alarm, skipping")
            metrics["escalation_missed_alarm"] += 1
            self.stop_sequence()
        if alarm.status == "A":
            logger.info("Alarm is not closed, skipping")
            metrics["escalation_not_closed"] += 1
            self.stop_sequence()
        return alarm

    def get_escalation_doc(self) -> Escalation:
        """
        Fetch current escalation doc to close
        """
        escalation_doc = Escalation.objects.filter(
            close_timestamp__exists=False, items__0__alarm=self.alarm.id
        ).first()
        if not escalation_doc:
            self.logger.error("Cannot find escalation document. Stopping")
            self.stop_sequence()
        # self.escalation_doc = escalation_doc
        return escalation_doc

    # TT System API
    def get_tt_system_context(self) -> TTSystemCtx:
        ctx = TTSystemCtx(
            id=self.tt_id,
            tt_system=self.tts.get_system(),
            queue=self.queue,
            reason=self.subject,
            login=self.login,
            is_unavailable=self.has_unavailable_alarm(),
        )
        return ctx

    def get_tts(self, tt_id: Optional[str]) -> Optional[TTSystem]:
        """
        Get TT System from tt_id
        """
        if not tt_id:
            return None
        tts_name = tt_id.split(":", 1)[0]
        tts = TTSystem.get_by_name(tts_name)
        if not tts:
            self.logger.info("Failed to add comment to %s: Invalid TT system", tts_name)
            metrics["escalation_tt_comment_fail"] += 1
            return None
        return tts

    def get_notification_group(
        self, notification_group_id: Optional[str]
    ) -> Optional[NotificationGroup]:
        """
        Get notification group by id.

        :returns: Notification group instance, if found, None otherwise
        """
        if not notification_group_id:
            return None
        return NotificationGroup.get_by_id(notification_group_id)

    def get_remote_tt_id(self) -> str:
        """
        Get remote tt id
        """
        return self.tt_id.split(":", 1)[1]

    def close_tt(self) -> None:
        """
        Close TT
        """
        if not self.tts:
            return
        with self.get_tt_system_context() as ctx:
            ctx.close(self.subject, self.body)
        r = ctx.get_result()
        if r.is_ok:
            metrics["escalation_tt_close"] += 1
            self.escalation_doc.leader.deescalation_status = "ok"
            self.alarm.close_escalation()
            return
        if r.status == EscalationStatus.TEMP:
            self.logger.info(
                "Temporary error detected while closing tt %s: %s", self.tt_id, r.error
            )
            metrics["escalation_tt_close_retry"] += 1
            self.tts.register_failure()
            self.alarm.set_escalation_close_error(
                "[%s] %s" % (self.alarm.managed_object.tt_system.name, r.error)
            )
            self.escalation_doc.leader.escalation_status = "temp"
            self.escalation_doc.leader.escalation_error = str(r.error)
            self.escalation_doc.save()
            self.retry_job(str(r.error))
        else:
            self.logger.info("Failed to close tt %s: %s", self.tt_id, r.error)
            metrics["escalation_tt_close_fail"] += 1
            self.alarm.set_escalation_close_error(
                "[%s] %s" % (self.alarm.managed_object.tt_system.name, r.error)
            )
            self.escalation_doc.leader.escalation_status = "fail"
            self.escalation_doc.leader.escalation_error = str(r.error)

    def comment_tt(self) -> None:
        """
        Append Comment to Trouble Ticket
        """
        if not self.tts:
            return
        self.logger.info("Appending comment to TT %s", self.tt_id)
        with self.get_tt_system_context() as ctx:
            ctx.comment(self.subject)
        r = ctx.get_result()
        if r.is_ok:
            metrics["escalation_tt_comment"] += 1
            self.escalation_doc.leader.deescalation_status = "ok"
            return
        if r.status == EscalationStatus.TEMP:
            self.logger.info("Failed to add comment to %s: %s", self.tt_id, r.errore)
            self.escalation_doc.leader.deescalation_status = "temp"
            self.escalation_doc.leader.deescalation_error = str(r.error)
            metrics["escalation_tt_comment_fail"] += 1
        else:
            self.logger.info("Failed to add comment to %s: %s", self.tt_id, r.error)
            self.escalation_doc.leader.deescalation_status = "fail"
            metrics["escalation_tt_comment_fail"] += 1
            self.escalation_doc.leader.deescalation_error = str(r.error)

    def deescalate_tt(self) -> None:
        """
        Close TT
        """
        if not self.tt_id:
            return
        self.alarm.set_escalation_close_ctx()
        if self.alarm.escalation_close_ts and self.escalation_doc.leader.escalation_status in {
            "ok",
            "fail",
        }:
            self.logger.info("Alarm is already deescalated")
            metrics["escalation_already_deescalated"] += 1
            return
        with Span(client="escalator", sample=PARENT_SAMPLE):
            c_tt_name, c_tt_id = self.tt_id.split(":")
            cts = TTSystem.get_by_name(c_tt_name)
            if not cts:
                self.logger.info("Failed to add comment to %s: Invalid TT system", self.tt_id)
                metrics["escalation_tt_comment_fail"] += 1
            if self.to_close_tt:
                self.close_tt()
            else:
                self.comment_tt()

    def notify(self) -> None:
        """
        Send notifications
        """
        if not self.notification_group:
            return
        self.log_alarm("Sending close notification to group %s" % self.notification_group.name)
        self.notification_group.notify(self.subject, self.body)
        metrics["escalation_notify"] += 1

    def has_active_alarms(self) -> bool:
        """
        Returns true if escalation doc has active alarms
        """
        alarm_ids = [a.alarm for a in self.escalation_doc.items]
        return bool(ActiveAlarm.objects.filter(id__in=alarm_ids))

    def has_unavailable_alarm(self) -> bool:
        """
        Return true if alarm is unavailable service
        :return:
        """
        return self.alarm.alarm_class.name == "NOC | Managed Object | Ping Failed"

    def process(self) -> None:
        """
        Perform deescalation sequence
        """
        with self.lock.acquire(self.escalation_doc.get_lock_items()):
            ts = datetime.datetime.now()
            self.deescalate_tt()
            self.notify()
            # Close escalation doc
            self.escalation_doc.close_timestamp = ts
            self.escalation_doc.save()
        # Run deescalation check when nessessary
        if self.has_active_alarms():
            call_later(
                "noc.services.escalator.escalation.check_close",
                scheduler="escalator",
                pool=self.alarm.managed_object.escalator_shard,
                delay=self.alarm.alarm_class.recover_time + ESCALATION_CHECk_CLOSE_DELAY,
                doc_id=str(self.escalation_doc.id),
            )


class CloseCheckSequence(BaseSequence):
    def __init__(self, doc_id: str):
        super().__init__(doc_id)
        self.escalation_doc = self.get_escalation_doc(doc_id)

    def get_escalation_doc(self, doc_id: str) -> Escalation:
        """
        Get escalation doc or stop the sequence
        """
        doc = Escalation.objects.filter(id=doc_id).first()
        if not doc:
            self.logger.error("Cannot find escalation doc. Stopping")
            self.stop_sequence()
        return doc

    def iter_active_alarms(self) -> Iterable[ActiveAlarm]:
        """
        Iterate the active alarms related to the escalation doc
        """
        alarm_ids = [i.alarm for i in self.escalation_doc.items]
        yield from ActiveAlarm.objects.filter(id__in=alarm_ids)

    def process(self):
        """
        Perform deescalation check. Run escalation sequence for all active alarms.
        """
        self.logger.info("[%s] Checking deescalation", self.escalation_doc.id)
        active_alarms = {a.id: a for a in self.iter_active_alarms()}
        if not active_alarms:
            self.logger.info("[%s] All alarms are cleared, stopping", self.escalation_doc.id)
            return
        for i in self.escalation_doc.items:
            alarm = active_alarms.get(i.alarm)
            if not alarm:
                continue
            if alarm.managed_object.tt_system.alarm_consequence_policy == "D":
                continue
            # Reescalate
            AlarmEscalation.watch_escalations(
                alarm,
                timestamp_policy=alarm.managed_object.tt_system.alarm_consequence_policy,
                defer=False,
                prev_escalation=str(self.escalation_doc.id),
            )
            i.deescalation_status = "reescalated"
        # Update escalation doc
        self.escalation_doc.save()


def escalate(
    alarm_id: str,
    escalation_id: str,
    escalation_delay: int,
    login: str = "correlator",
    timestamp_policy: str = "a",
    force: bool = False,
    prev_escalation: Optional[str] = None,
    *args,
    **kwargs,
):
    """
    Delayed job to start escalation process. Wrapper for EscalationSequence
    """
    try:
        EscalationSequence(
            alarm_id=alarm_id,
            escalation_id=escalation_id,
            escalation_delay=escalation_delay,
            login=login,
            timestamp_policy=timestamp_policy,
            force=force,
            prev_escalation=prev_escalation,
        ).run()
    except BaseSequence.StopSequence:
        pass


def notify_close(
    alarm_id: str,
    tt_id: str,
    subject: str,
    body: str,
    notification_group_id: Optional[str] = None,
    close_tt: bool = False,
    login: str = "correlator",
    queue: Optional[str] = None,
):
    try:
        DeescalationSequence(
            alarm_id=alarm_id,
            tt_id=tt_id,
            subject=subject,
            body=body,
            notification_group_id=notification_group_id,
            close_tt=close_tt,
            login=login,
            queue=queue,
        ).run()
    except BaseSequence.StopSequence:
        pass


def check_close(doc_id: str) -> None:
    """
    Check all nested alarms are closed, reescalate when necessary
    """
    try:
        CloseCheckSequence(doc_id=doc_id).run()
    except BaseSequence.StopSequence:
        pass
