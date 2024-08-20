# ---------------------------------------------------------------------
# Escalation model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
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
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_DOWNLINK_MERGE
from noc.core.tt.types import EscalationStatus, TTAction, EscalationMember
from noc.core.scheduler.job import Job
from noc.aaa.models.user import User
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.sa.models.service import Service
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
        managed_object: Alarm managed_object
        target_reference: Unique resource key
        alarm: Alarm Id item
        status: Item status
    """

    meta = {"strict": False}
    managed_object = ForeignKeyField(ManagedObject)
    target_reference = BinaryField(required=False)
    alarm = ObjectIdField()
    status = EnumField(ItemStatus, default=ItemStatus.NEW)
    # Already escalated doc

    def __str__(self) -> str:
        return f"{self.managed_object.name}:{self.alarm}"

    @property
    def is_new(self) -> bool:
        """
        Check if item is new (no escalation attempts)
        """
        return self.status == ItemStatus.NEW

    @property
    def is_already_escalated(self) -> bool:
        """
        Check if item is already escalated
        """
        return self.status == ItemStatus.EXISTS


class EscalationLog(EmbeddedDocument):
    """
    Escalation Log item
    Attributes:
        timestamp: Escalation Timestamp
        member: Escalation member
        key: Member Id
        document_id: Escalation ID on TTSystem
        repeats: Escalation runs count
        status: Escalation Status
        error: Error when status is not ok
        deescalation_status: End escalation status on TT System
        deescalation_error: Error on deescalation process
    """

    meta = {"strict": False}

    timestamp = DateTimeField()
    member = EnumField(EscalationMember, required=True)
    key: str = StringField(required=True)
    document_id = StringField()
    repeats: int = IntField(default=0)
    # Approve flag (is user Approved Received Message)
    # Notification adapter for sender
    template = StringField(required=False)
    # Wait handler
    status: EscalationStatus = EnumField(EscalationStatus)
    error = StringField()
    deescalation_status: EscalationStatus = EnumField(EscalationStatus)
    deescalation_error = StringField()

    def __str__(self):
        if self.deescalation_status:
            return f"{self.timestamp}: {self.member}, {self.status}/{self.deescalation_status}"
        return f"{self.timestamp}: {self.member}, {self.status}"


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
    profile: EscalationProfile = PlainReferenceField(EscalationProfile)
    prev_profile = ObjectIdField()  # prev_escalation
    # Start escalation timestamp
    timestamp: datetime.datetime = DateTimeField(default=datetime.datetime.now)
    end_timestamp = DateTimeField()
    # Escalation context
    ctx_id: int = LongField(required=False)  # Ctx
    sequence_num: int = IntField(min_value=0, default=0)
    # Document options
    is_dirty = BooleanField(default=True)  # Set if items was changed, Calculate by status
    forced = BooleanField(default=False)
    # Escalation Item and Escalation Log
    items: List[EscalationItem] = EmbeddedDocumentListField(EscalationItem)
    escalations: List[EscalationLog] = EmbeddedDocumentListField(EscalationLog)
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
        return f"{self.profile.name} ({self.sequence_num}): {str(self.id)}"

    def get_timestamp(self) -> datetime.datetime:
        if not self.sequence_num:
            return self.timestamp
        delay = sum(i.delay for i in self.profile.escalations[0 : self.sequence_num])
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
        return self.items[0]

    @property
    def consequences(self) -> List[EscalationItem]:
        return self.items[1:]

    @property
    def alarm(self) -> Optional[ActiveAlarm]:
        return get_alarm(self.items[0].alarm)

    @property
    def managed_object(self) -> Optional[ManagedObject]:
        return self.items[0].managed_object

    @property
    def service(self) -> Optional[Service]:
        if not self.affected_services:
            return None
        return Service.objects.filter(id=self.affected_services[0]).first()

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
                seconds=(self.profile.escalations[-1].delay + self.profile.repeat_delay) * repeat
            )
        else:
            repeat_delay = datetime.timedelta(seconds=0)
        next_esc = self.profile.escalations[sequence_num]
        seq_delay = datetime.timedelta(seconds=int(next_esc.delay))
        return self.timestamp + repeat_delay + seq_delay

    def get_repeat(self) -> int:
        """Getting Repeat number"""
        r = []
        for i in self.escalations:
            if not i.repeats:
                continue
            r.append(i.repeats)
        return min(r) if r else 0

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
        template: Optional[str] = None,
    ):
        """
        Args:
            member: Escalation type
            key: Escalation Key
            status: Escalation result status
            timestamp: Escalation time
            error: Error message
            document_id: TT System document ID
            template: Create TT Template
        """
        timestamp = timestamp or datetime.datetime.now().replace(microsecond=0)
        key = str(key)
        for esc in self.escalations:
            if member == esc.member and key == esc.key:
                esc.status = status
                esc.error = error
                if document_id:
                    esc.document_id = document_id
                break
        else:
            self.escalations.append(
                EscalationLog(
                    timestamp=timestamp,
                    key=key,
                    member=member,
                    status=status,
                    document_id=document_id,
                    template=template,
                )
            )

    def get_escalation(self, member: EscalationMember, key: str) -> Optional[EscalationLog]:
        """
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
        affected = alarm.affected_services
        groups = alarm.groups
        if not alarm.affected_services and "service" in alarm.vars:
            affected = [alarm.vars["service"]]
            groups = [alarm.reference]
        return Escalation(
            timestamp=ts,
            profile=profile,
            severity=alarm.severity,
            groups=groups,
            affected_services=affected,
            forced=force,
            items=[
                EscalationItem(
                    alarm=alarm.id,
                    target_reference=str(alarm.managed_object.bi_id).encode(),
                    managed_object=alarm.managed_object,
                )
            ],
        )

    @classmethod
    def ensure_job(cls, eid: str):
        """Update Job, TTSystem Shard (Set Shard on Profile)"""
        Job.submit("escalator", ESCALATION_JOB, key=str(eid), pool="default")

    @classmethod
    def register_item_changes(cls, item_id, from_statuses: List[ItemStatus], to_status: ItemStatus):
        """Register item change"""
        coll = Escalation._get_collection()
        r = coll.find_one_and_update(
            {
                "items.0.alarm": item_id,
                "items.0.status": {"$in": [i.value for i in from_statuses]},
                # "is_dirty": False,
                "end_timestamp": {"$exists": False},
            },
            {"$set": {"items.0.status": to_status.value, "is_dirty": True}},
            projection={"end_timestamp": True, "_id": True},
        )
        logger.debug("[%s] Register changes on Escalation Document", r.get("_id"))
        if r:
            # Update Job, TTSystem Shard (Set Shard on Profile)
            # Job.submit("escalator", ESCALATION_JOB, key=str(r["_id"]), pool="default")
            cls.ensure_job(r["_id"])

    def update_summary(self):
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
        policy = self.profile.escalation_policy.name.lower()
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

    def get_tt_ids(self) -> str:
        """Return all escalated Document with TT system"""
        r = []
        for i in self.escalations:
            if i.member == EscalationMember.TT_SYSTEM and i.document_id:
                tt = TTSystem.get_by_id(i.key)
                r.append(f"{tt.name}:{i.document_id}")
        return ";".join(r)

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
        if self.profile.end_condition == "CR":
            return self.leader.status == ItemStatus.REMOVED
        elif self.profile.end_condition == "CA":
            return all(i.status == ItemStatus.REMOVED for i in self.items)
        elif self.profile.end_condition == "CT":
            # Close TT
            return self.escalations and self.escalations[0].deescalation_status == "ok"
        elif self.profile.end_condition == "M":
            return bool(self.end_timestamp)
        return False
