# ---------------------------------------------------------------------
# Escalation model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import datetime
import logging
import enum
from collections import defaultdict
from typing import List, Set, Iterable, Optional, DefaultDict

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BinaryField,
    DateTimeField,
    ListField,
    LongField,
    EnumField,
    IntField,
    EmbeddedDocumentListField,
    ObjectIdField,
    BooleanField,
)
from bson import ObjectId

# NOC modules
from noc.core.mongo.fields import ForeignKeyField
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.tt.types import EscalationStatus, TTAction, EscalationMember, EscalationRequest
from noc.core.models.escalationpolicy import EscalationPolicy
from noc.core.scheduler.job import Job
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.template import Template
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.ttsystem import TTSystem
from noc.fm.models.utils import get_alarm
from .escalationprofile import EscalationProfile

logger = logging.getLogger(__name__)
ESCALATION_JOB = "noc.services.escalator.jobs.escalation.EscalationJob"
CHECK_TT_JOB = "noc.services.escalator.jobs.check_tt.CheckTTJob"


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


class EscalationItem(EmbeddedDocument):
    """
    Escalation affected items. First item it escalation leader
    Attributes:
        managed_object_id: Alarm managed_object
        target_reference: Unique resource key
        alarm: Alarm Id item
        status: Item status
    """

    meta = {"strict": False}
    managed_object_id: int = IntField()
    target_reference = BinaryField(required=False)
    alarm = ObjectIdField()
    status = EnumField(ItemStatus, default=ItemStatus.NEW)
    # Already escalated doc

    def __str__(self) -> str:
        return f"{self.managed_object.name}:{self.alarm}"

    @property
    def managed_object(self) -> "ManagedObject":
        """"""
        return ManagedObject.get_by_id(self.managed_object_id)

    @property
    def is_new(self) -> bool:
        """Check if item is new (no escalation attempts)"""
        return self.status == ItemStatus.NEW

    @property
    def is_already_escalated(self) -> bool:
        """Check if item is already escalated"""
        return self.status == ItemStatus.EXISTS

    @property
    def is_maintenance(self) -> bool:
        """Check ManagedObject in Maintenance"""
        return self.managed_object.in_maintenance


class EscalationStep(EmbeddedDocument):
    """
    Escalation Log item
    Attributes:
        timestamp: Escalation Timestamp
        member: Escalation member
        key: Member Id
        document_id: Escalation ID on TTSystem
        retries: Escalation runs count
        status: Escalation Status
        error: Error when status is not ok
        deescalation_status: End escalation status on TT System
        deescalation_error: Error on deescalation process
    """

    meta = {"strict": False}

    timestamp = DateTimeField()
    delay: int = IntField(default=0)
    member = EnumField(EscalationMember, required=True)
    key: str = StringField(required=True)
    ack_policy: str = StringField(
        choices=[
            ("ack", "Alarm Acknowledge"),
            ("nack", "Alarm not Acknowledge"),
            # wait ack ?
            ("any", "Any Acknowledge"),
        ],
        default="any",
    )
    time_pattern = StringField(required=False)
    min_severity = IntField(default=0)
    #
    max_retries: int = IntField(default=1)
    retries: int = IntField(default=0)
    # Approve flag (is user Approved Received Message)
    # Notification adapter for sender
    stop_processing = BooleanField(default=False)
    # Wait handler
    template: Template = ForeignKeyField(Template)
    document_id = StringField()
    status: EscalationStatus = EnumField(EscalationStatus, default=EscalationStatus.NEW)
    error = StringField()
    # Deescalation Block
    close_template: Template = ForeignKeyField(Template)
    deescalation_status: EscalationStatus = EnumField(EscalationStatus)
    deescalation_error = StringField()

    def __str__(self):
        if self.deescalation_status:
            return f"{self.timestamp}: {self.member}, {self.status}/{self.deescalation_status}"
        return f"{self.timestamp}: {self.member}, {self.status}"

    @property
    def notification_group(self) -> Optional[NotificationGroup]:
        if self.member == EscalationMember.NOTIFICATION_GROUP:
            return NotificationGroup.get_by_id(int(self.key))

    @property
    def tt_system(self) -> Optional["TTSystem"]:
        if self.member == EscalationMember.TT_SYSTEM:
            return TTSystem.get_by_id(self.key)

    def set_status(
        self,
        status: EscalationStatus,
        error: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        document_id: Optional[str] = None,
    ):
        """"""
        ts = timestamp or datetime.datetime.now().replace(microsecond=0)
        self.status = status
        self.timestamp = ts
        self.error = error
        if error:
            self.error = error
        if document_id:
            self.document_id = document_id

    @property
    def create_tt(self):
        return self.member == EscalationMember.TT_SYSTEM


class ActionLog(EmbeddedDocument):
    """
    Attributes:
        status: Action Status
        action: Action type
        user: User for action
        contact: Receiver address
        message: Notify/comment message
    """

    timestamp = DateTimeField()
    status: EscalationStatus = EnumField(EscalationStatus)
    # ack_alarm, close_alarm, add_comment ? User
    action: TTAction = EnumField(TTAction, required=True)
    # User Actions
    user: Optional["User"] = ForeignKeyField(User, required=False)
    contact: Optional[str] = StringField()
    message: Optional[str] = StringField()


class Escalation(Document):
    meta = {
        "collection": "escalations",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "items.alarm",
            "end_timestamp",
            "items.0.alarm",
            "escalations.document_id",
            ("end_timestamp", "items.0.alarm", "items.0.status", "is_dirty"),
            # ("end_timestamp", "items.alarm", "escalations.member"),
            {"fields": ["expires"], "expireAfterSeconds": 0},
        ],
    }
    # profile: EscalationProfile = PlainReferenceField(EscalationProfile)
    # prev_profile = ObjectIdField()  # prev_escalation
    # Start escalation timestamp
    name = StringField()
    escalation_policy = EnumField(EscalationPolicy, default=EscalationPolicy.ROOT)
    timestamp: datetime.datetime = DateTimeField(default=datetime.datetime.now)
    end_timestamp = DateTimeField()
    # Escalation context
    ctx_id: int = LongField(required=False)  # Ctx
    sequence_num: int = IntField(min_value=0, default=0)
    # Repeat
    repeats: int = IntField(default=0)
    repeat_delay: int = IntField(default=60)
    # Policy
    end_condition = StringField(
        required=True,
        choices=[
            ("CR", "Close Root"),
            ("CA", "Close All"),
            ("E", "End Chain"),
            ("CT", "Close TT"),  # By Adapter
            ("M", "Manual"),  # By Adapter
        ],
        default="CR",
    )
    # Document options
    is_dirty = BooleanField(default=True)  # Set if items was changed, Calculate by status
    forced = BooleanField(default=False)
    telemetry_sample = IntField(default=0)
    # Escalation Item and Escalation Log
    items: List[EscalationItem] = EmbeddedDocumentListField(EscalationItem)
    escalations: List[EscalationStep] = EmbeddedDocumentListField(EscalationStep)
    actions: List[ActionLog] = EmbeddedDocumentListField(ActionLog)
    # List of group references, if any
    groups = ListField(BinaryField())
    affected_services = ListField(ObjectIdField())
    # affected_maintenances = ListField(ObjectIdField())
    # Escalation summary
    severity: int = IntField(min_value=0)
    subject: Optional[str] = StringField(required=False)
    total_objects: List[ObjectSummaryItem] = EmbeddedDocumentListField(ObjectSummaryItem)
    total_services: List[SummaryItem] = EmbeddedDocumentListField(SummaryItem)
    total_subscribers: List[SummaryItem] = EmbeddedDocumentListField(SummaryItem)
    expires = DateTimeField(required=False)
    # Labels ?
    # ttl - ttl field with index

    def __str__(self) -> str:
        return f"{self.name} ({self.sequence_num}): {str(self.id)}"

    def get_timestamp(self) -> datetime.datetime:
        if not self.sequence_num:
            return self.timestamp
        delay = sum(i.delay for i in self.escalations[0 : self.sequence_num])
        return self.timestamp + datetime.timedelta(seconds=delay)

    def get_lock_items(self) -> List[str]:
        s: Set[str] = set()
        # Add items
        for item in self.items:
            s.add(f"a:{item.alarm}")
        # Add references
        if self.groups:
            for group in self.groups:
                s.add(f"g:{group}")
        return list(s)

    @property
    def leader(self) -> EscalationItem:
        """Escalation Leader - First"""
        for ii in self.items:
            if ii.status == ItemStatus.REMOVED:
                continue
            return ii
        return self.items[0]

    @property
    def tt_id(self) -> str:
        """Return first TT ID"""
        r = self.get_tt_ids()
        return r[0]

    @property
    def consequences(self) -> List[EscalationItem]:
        return self.items[1:]

    @property
    def alarm(self) -> Optional[ActiveAlarm]:
        return get_alarm(self.leader.alarm)

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        for ii in self.items:
            if ii.status == ItemStatus.REMOVED:
                return ii.managed_object
        return self.leader.managed_object

    @property
    def service(self) -> Optional[Service]:
        if not self.affected_services:
            return None
        return Service.get_by_id(self.affected_services[0])

    def get_next(
        self, sequence_num: Optional[int] = None, repeat: Optional[int] = None
    ) -> datetime.datetime:
        """
        Calculate next step timestamp

        Args:
            sequence_num: Number of sequence step
            repeat: Number of repeats
        """
        # Check end
        if sequence_num is None:
            sequence_num = self.sequence_num
        repeat = repeat or self.get_repeat()
        # Repeat
        if repeat:
            repeat_delay = datetime.timedelta(
                seconds=(self.escalations[-1].delay + self.repeat_delay) * repeat
            )
        else:
            repeat_delay = datetime.timedelta(seconds=0)
        next_esc = self.escalations[sequence_num]
        seq_delay = datetime.timedelta(seconds=int(next_esc.delay))
        return self.timestamp + repeat_delay + seq_delay

    def get_repeat(self) -> int:
        """Getting Repeat number"""
        return self.repeats

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

    def set_escalation_context(self):
        """Set escalation SPAN Id"""
        current_context, current_span = get_current_span()
        if current_context or self.ctx_id:
            self.ctx_id = current_context
            self._get_collection().update_one(
                {"_id": self.id}, {"$set": {"ctx_id": current_context}}
            )

    def has_merged_downlinks(self) -> bool:
        """
        Check if alarm has merged downlinks
        """
        # ! replace on consequence
        if not self.alarm:
            return False
        return bool(
            ActiveAlarm.objects.filter(root=self.alarm.id, rca_type=RCA_DOWNLINK_MERGE).first()
        )

    def get_ctx(self):
        """Get escalation context for render templite"""
        from noc.sa.models.serviceprofile import ServiceProfile
        from noc.sa.models.managedobjectprofile import ManagedObjectProfile
        from noc.crm.models.subscriberprofile import SubscriberProfile

        # affected_objects = sorted(self.alarm.iter_affected(), key=operator.attrgetter("name"))
        affected_objects = sorted(
            [i.managed_object for i in self.items],
            key=operator.attrgetter("name"),
        )
        if self.affected_services:
            affected_services = list(Service.objects.filter(id__in=self.affected_services))
        else:
            affected_services = []
        segment = self.managed_object.segment
        if segment.is_redundant:
            uplinks = self.managed_object.uplinks
            lost_redundancy = len(uplinks) > 1
            total_affected_subscribers = self.summary_to_list(
                segment.total_subscribers, SubscriberProfile
            )
            total_affected_services = self.summary_to_list(segment.total_services, ServiceProfile)
        else:
            lost_redundancy = False
            total_affected_subscribers = []
            total_affected_services = []
        cons_escalated = [get_alarm(x.alarm) for x in self.consequences if x.is_already_escalated]
        return {
            "alarm": self.alarm,
            "managed_object": self.managed_object,
            "service": self.service if self.service else None,
            "affected_objects": affected_objects,
            "cons_escalated": cons_escalated,
            "total_objects": self.summary_to_list(self.alarm.total_objects, ManagedObjectProfile),
            "total_subscribers": self.summary_to_list(
                self.alarm.total_subscribers, SubscriberProfile
            ),
            "total_services": self.summary_to_list(self.alarm.total_services, ServiceProfile),
            "tt": None,
            "severity": self.severity,
            "lost_redundancy": lost_redundancy,
            "affected_services": affected_services,
            "total_affected_subscribers": total_affected_subscribers,
            "total_affected_services": total_affected_services,
            "has_merged_downlinks": self.has_merged_downlinks(),
        }

    def iter_alarms_never(self) -> Iterable[ActiveAlarm]:
        """
        `never` escalation policy. Yields not items
        """
        logger.info("[%s] Escalation is denied by policy", self.id)
        yield from []

    def iter_alarms_root(self) -> Iterable[ActiveAlarm]:
        """
        `root` escalation policy. If alarm is root cause, yield root alarm
        and all the consequences
        """
        if self.alarm.root:
            logger.info("[%s|root] Alarm is not a root cause. Skipping", self.id)
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
            logger.info("[%s][root_first] Alarm is not a root cause. Skipping", self.id)
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

    def set_item_status(
        self,
        alarm: ActiveAlarm,
        status: ItemStatus = ItemStatus.NEW,
        error: Optional[str] = None,
    ):
        """
        Set status for Escalation Item

        Args:
            alarm: Alarm for item
            status: Status
            error: Error text for Status
        """
        for item in self.items:
            if str(item.alarm) == str(alarm.id) and status != ItemStatus.NEW:
                item.status = status
                break
            elif str(item.alarm) == str(alarm.id):
                break
        else:
            self.items += [
                EscalationItem(
                    managed_object=alarm.managed_object,
                    # target_reference=
                    alarm=alarm.id,
                    status=status,
                )
            ]

    def set_escalation(
        self,
        member: EscalationMember,
        key: str,
        status: EscalationStatus,
        timestamp: Optional[datetime.datetime] = None,
        error: Optional[str] = None,
        document_id: Optional[str] = None,
    ):
        """
        Args:
            member: Escalation type
            key: Escalation Key
            status: Escalation result status
            timestamp: Escalation time
            error: Error message
            document_id: TT System document ID
        """
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        key = str(key)
        for esc in self.escalations:
            if member == esc.member and key == esc.key:
                esc.status = status
                esc.error = error
                esc.timestamp = timestamp
                if document_id:
                    esc.document_id = document_id
                break

    def get_escalation(self, member: EscalationMember, key: str) -> Optional[EscalationStep]:
        """
        get_step
        Getting escalation log for item

        Args:
            member: Escalation member
            key: Action ky
        """
        for item in self.escalations:
            if item.member == member and item.key == key:
                return item
        return None

    def set_action(
        self,
        action: TTAction,
        status: EscalationStatus,
        user: Optional[User] = None,
        contact: Optional[str] = None,
        message: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        error: Optional[str] = None,
    ):
        """
        Args:
            action: Escalation type
            status: Escalation result status
            user: User action, set User
            contact: Notify Action - set recipient
            message: Message for sent
            timestamp: Escalation time
            error: Error message
        """
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        for a in self.actions:
            if action == a.action:
                a.status = status
                a.error = error
                break
        else:
            self.actions.append(
                ActionLog(
                    timestamp=timestamp,
                    user=user,
                    message=message,
                    action=action,
                    status=status,
                )
            )

    def get_action(self, action: TTAction, user: Optional[User] = None) -> Optional[ActionLog]:
        """
        Getting escalation log for item

        Args:
            action: Escalation Action
            user: Action ky
        """
        for item in self.actions:
            if user and item.user != user:
                continue
            if item.action == action:
                return item
        return None

    @classmethod
    def register_escalation(
        cls, alarm: ActiveAlarm, profile: EscalationProfile, force: bool = False
    ):
        """Register new alarm escalation"""
        ed = Escalation.from_alarm(alarm, profile, force=force)
        ed.save()
        # ActiveAlarm.objects.filter(id=alarm.id).update(escalation_profile=profile)
        alarm.escalate(ed)
        Job.submit(
            "escalator",
            ESCALATION_JOB,
            ts=ed.timestamp,
            key=str(ed.id),
            pool=alarm.managed_object.escalator_shard or "default",
        )

    @classmethod
    def from_alarm(
        cls,
        alarm: ActiveAlarm,
        profile: EscalationProfile,
        force: bool = False,
    ) -> "Escalation":
        """
        Create Escalation instance from alarm and profile
        Args:
            alarm: ActiveAlarm instance
            profile: Escalation Profile
            force: Forced escalation
        """
        if profile.alarm_consequence_policy == "c":
            ts = datetime.datetime.now()
        else:
            ts = alarm.timestamp
        req = EscalationProfile.get_job(profile, timestamp=ts)
        doc = Escalation.from_request(req)
        doc.severity = (alarm.severity,)
        if not alarm.affected_services and "service" in alarm.vars:
            doc.affected_services = [alarm.vars["service"]]
            doc.groups = [alarm.reference]
        else:
            doc.affected_services = alarm.affected_services
            doc.groups = alarm.groups
        doc.items = [
            EscalationItem(
                alarm=alarm.id,
                target_reference=str(alarm.managed_object.bi_id).encode(),
                managed_object=alarm.managed_object,
            )
        ]
        return doc

    @classmethod
    def from_request(cls, request: EscalationRequest, force: bool = False) -> "Escalation":
        """"""
        doc = Escalation(
            timestamp=request.timestamp,
            name=request.name,
            escalation_policy=request.items_policy,
            end_condition=request.end_condition,
            forced=force,
        )
        for step in request.steps:
            doc.escalations.append(
                EscalationStep(
                    delay=step.delay,
                    member=step.member,
                    key=step.key,
                    ack_policy=step.ack,
                    time_pattern=step.time_pattern,
                    min_severity=step.min_severity,
                    max_retries=step.max_retries,
                    stop_processing=step.stop_processing,
                    template=step.template,
                    close_template=step.close_template,
                )
            )
        if request.repeat_policy == "D":
            doc.repeats = 1
        return doc

    @classmethod
    def ensure_job(cls, eid: str):
        """Update Job, TTSystem Shard (Set Shard on Profile)"""
        Job.submit("escalator", ESCALATION_JOB, key=str(eid), pool="default")

    @classmethod
    def register_changes(
        cls,
        item_id,
        to_status: Optional[ItemStatus] = None,
        from_statuses: Optional[List[ItemStatus]] = None,
    ):
        """
        Register item change
        * for item_id - set is_dirty and ensure_job
        * for to_state:
            * ItemStatus.Removed - close alarm, set status, is_dirty and ensure_job
            * ItemStatus.New - reopen alarm, set_status, is_dirty, clean end_escalation
        """
        coll = Escalation._get_collection()

        q = {"items.0.alarm": item_id, "is_dirty": False, "end_timestamp": {"$exists": False}}
        q_set = {"is_dirty": True}
        if to_status:
            q_set["items.0.status"] = to_status.value
            if to_status == ItemStatus.NEW:
                # Reopen alarm
                q_set = {"$unset": {"end_timestamp": True}}
        r = coll.find_one_and_update(
            q,
            {"$set": q_set},
            projection={"end_timestamp": True, "sequence_num": True, "_id": True},
        )
        if r and r["sequence_num"]:
            logger.debug("[%s] Register changes on Escalation Document", r.get("_id"))
            # Update Job, TTSystem Shard (Set Shard on Profile)
            # Job.submit("escalator", ESCALATION_JOB, key=str(r["_id"]), pool="default")
            cls.ensure_job(r["_id"])

    def update_items(self):
        """Update escalation doc items. Run on is_dirty"""

        def update_totals_from_summary(
            t_dict: DefaultDict[ObjectId, int], t_items: Iterable[SummaryItem]
        ) -> None:
            """
            Update totals from alarm summary
            """
            for item in t_items:
                t_dict[item.profile] += item.summary

        # Dynamic (save to field)
        policy = self.escalation_policy
        iter_items = getattr(self, f"iter_alarms_{policy}", None)
        if not iter_items:
            logger.error("Unknown escalation policy `%s`. Skipping", policy)
            return None
        items = list(iter_items())
        if not items:
            return None
        # Total counters
        total_objects: DefaultDict[int, int] = defaultdict(int)
        total_services: DefaultDict[ObjectId, int] = defaultdict(int)
        total_subscribers: DefaultDict[ObjectId, int] = defaultdict(int)
        # @todo: Append profile
        for alarm in items:
            if alarm.alarm_class.is_ephemeral:
                # Group alarms are virtual and should be locked, but not escalated
                self.groups += [alarm.reference]
                continue
            if alarm.status == "C":
                self.set_item_status(alarm, ItemStatus.REMOVED)
            else:
                self.set_item_status(alarm, ItemStatus.NEW)
            # Update totals
            total_objects[alarm.managed_object.object_profile.id] += 1
            update_totals_from_summary(total_services, alarm.direct_services)
            update_totals_from_summary(total_subscribers, alarm.direct_subscribers)

        # if not self.items:
        #    return None  # Only group alarms
        self.total_objects = [
            ObjectSummaryItem(profile=k, summary=v) for k, v in total_objects.items()
        ]
        self.total_services = [SummaryItem(profile=k, summary=v) for k, v in total_services.items()]
        self.total_subscribers = [
            SummaryItem(profile=k, summary=v) for k, v in total_subscribers.items()
        ]

    def get_tt_ids(self) -> List[str]:
        """Return all escalated Document with TT system"""
        r = []
        for i in self.escalations:
            if i.member == EscalationMember.TT_SYSTEM and i.document_id:
                tt = TTSystem.get_by_id(i.key)
                r.append(f"{tt.name}:{i.document_id}")
        return r

    def get_item_by_key(self, key: str) -> Optional[EscalationItem]:
        for ii in self.profile.escalations:
            if ii.get_key() == key:
                return ii
        return

    def check_end(self) -> bool:
        """
        Check Escalation End Condition:
            * CR - Close Alarm Leader
            * CA - Close All alarm on escalation
            * CT - Close TT System Document (forced), supported get TT info
            * M - Manual Escalation Close (from alarm forced, set end_timestamp)
        """
        if self.end_timestamp or self.alarm.status != "A":
            return True
        # Check if alarm leader was closed
        if self.end_condition == "CR":
            return self.leader.status == ItemStatus.REMOVED
        elif self.end_condition == "CA":
            return all(i.status == ItemStatus.REMOVED for i in self.items)
        elif self.end_condition == "CT":
            # Close TT
            return self.escalations and self.escalations[0].deescalation_status == "ok"
        elif self.end_condition == "M":
            return bool(self.end_timestamp)
        return False
