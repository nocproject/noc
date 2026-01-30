# ---------------------------------------------------------------------
# Alarm Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from enum import Enum
from typing import Iterable, List, Optional

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ObjectIdField,
    EmbeddedDocumentListField,
    EnumField,
    DateTimeField,
    DictField,
    LongField,
    FloatField,
    ListField,
    BinaryField,
    IntField,
)

# NOC models
from noc.core.fm.enum import AlarmAction, ActionStatus, ItemStatus
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem


class JobStatus(Enum):
    """
    Job status.

    Attributes:
        * `p` - Pending, waiting for manual approve.
        * `w` - Waiting, ready to run.
        * `r` - Running
        * `S` - Suspended
        * `s` - Success
        * `f` - Failed with error
        * `w` - Warning. Failed, but allowed to fail.
        * `c` - Cancelled
    """

    PENDING = "p"
    WAITING = "w"
    RUNNING = "r"
    SUSPENDED = "S"
    SUCCESS = "s"
    FAILED = "f"
    WARNING = "W"
    CANCELLED = "c"


class GroupItem(EmbeddedDocument):
    reference = StringField()
    id: StringField(required=True)


class AlarmItem(EmbeddedDocument):
    """
    Escalation affected items. First item it escalation leader
    Attributes:
        alarm: Alarm Id item
        status: Item status
    """

    meta = {"strict": False}

    alarm = ObjectIdField()
    # For requested Escalation by ManagedObject
    # managed_object_id: Int
    status = EnumField(ItemStatus, default=ItemStatus.NEW)
    # Already escalated doc


class ActionLog(EmbeddedDocument):
    """
    Attributes:
        status: Action Status
        action: Action type
        user: User for action
    """

    meta = {"strict": False}

    timestamp = DateTimeField(required=True)
    action: AlarmAction = EnumField(AlarmAction, required=True)
    key: str = StringField()
    # Message
    template: Optional[str] = StringField(required=False)
    subject: str = StringField()
    # Status
    status: ActionStatus = EnumField(ActionStatus, default=ActionStatus.NEW)
    error: Optional[str] = StringField()
    document_id = StringField()
    # Condition
    min_severity: int = IntField(default=0)
    time_pattern = StringField()
    alarm_ack = StringField()
    when = StringField(default="any")
    stop_processing: bool = BooleanField(default=False)
    allow_fail: bool = BooleanField(default=False)
    repeat_num: int = IntField(default=0)
    # policy: GroupPolicy = EnumField(GroupPolicy, default=GroupPolicy.ROOT)
    # Approve flag (is user Approved Received Message)
    # Notification adapter for sender
    # User Actions
    user: Optional[int] = IntField()
    tt_system: Optional[str] = StringField()
    ctx = DictField()


class AlarmJob(Document):
    """
    Pipeline job.

    Attributes:
        name: Name, when parent is not empty, must be unique
            within parent.
        description: Optional description.
        status: See JobStatus for values.
        created_at: Creation timestamp.
        started_at: A timestamp when the job is entered Running state.
        completed_at: A timestamp when the job is leaved Runnig state.
    """

    meta = {
        "collection": "alarmjobs",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            {"fields": ["expires"], "expireAfterSeconds": 0},
        ],
    }
    name = StringField(required=True)
    description = StringField()
    # labels = ListField(StringField())
    # effective_labels = ListField(StringField())
    status = EnumField(JobStatus, default=JobStatus.WAITING, required=True)
    escalation_profile = ObjectIdField(required=False)
    # Start escalation timestamp
    created_at = DateTimeField(required=True)
    started_at = DateTimeField(required=False)
    completed_at = DateTimeField(required=False)
    # Escalation context
    ctx_id: int = LongField(required=False)  # Ctx
    telemetry_sample: int = FloatField(default=0)
    end_condition: str = StringField()
    maintenance_policy: str = StringField()
    # Document options
    items: List[AlarmItem] = EmbeddedDocumentListField(AlarmItem)
    actions: List[ActionLog] = EmbeddedDocumentListField(ActionLog)
    # List of group references, if any
    tt_docs = DictField()
    is_dirty = BooleanField(default=True)
    groups = ListField(BinaryField())
    max_repeats: int = IntField(default=0)
    repeat_delay: int = IntField(default=60)
    affected_services = ListField(ObjectIdField())
    affected_maintenances = ListField(ObjectIdField())
    # Escalation summary
    severity: int = IntField(min_value=0)
    # subject: Optional[str] = StringField(required=False)
    total_objects: List[ObjectSummaryItem] = EmbeddedDocumentListField(ObjectSummaryItem)
    total_services: List[SummaryItem] = EmbeddedDocumentListField(SummaryItem)
    total_subscribers: List[SummaryItem] = EmbeddedDocumentListField(SummaryItem)
    expires = DateTimeField(required=False)

    def __str__(self) -> str:
        return f"{self.name}::{self.status}"

    @classmethod
    def iter_last_for_entities(cls, entities: Iterable[str]) -> Iterable["AlarmJob"]:
        """
        Iterate last jobs for entities.

        Args:
            entities: Iterable of entity strings.

        Returns:
            Yield last jobs for entitites.
        """
        ids = [
            x["_id"]
            for x in cls._get_collection().aggregate(
                [
                    # Filter entities
                    {"$match": {"entity": {"$in": list(entities)}}},
                    {
                        "$sort": {"entity": 1, "_id": -1},
                    },
                    {"$group": {"_id": "$entity", "max_id": {"$first": "$_id"}}},
                    {"$project": {"_id": "$max_id"}},
                ]
            )
        ]
        yield from cls.objects.filter(id__in=ids)
