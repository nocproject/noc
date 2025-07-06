# ---------------------------------------------------------------------
# Escalation Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
from typing import Iterable, List, Optional


# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    BooleanField,
    ObjectIdField,
    EmbeddedDocumentListField,
    EnumField,
    DateTimeField,
    DictField,
    LongField,
    FloatField,
    IntField,
    BinaryField,
)

# NOC models
from noc.core.tt.types import EscalationGroupPolicy, TTAction
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.services.escalator.types import JobStatus, ActionStatus, ItemStatus


class GroupItem(EmbeddedDocument):
    reference = StringField()
    id: StringField(required=True)


class EscalationItem(EmbeddedDocument):
    """
    Escalation affected items. First item it escalation leader
    Attributes:
        alarm: Alarm Id item
        status: Item status
    """

    meta = {"strict": False}

    alarm = ObjectIdField()
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
    action: TTAction = EnumField(TTAction, required=True)
    status: ActionStatus = EnumField(ActionStatus, required=True)
    key: str = StringField()
    document_id = StringField()
    # Condition
    min_severity: int = IntField(default=0)
    time_pattern = StringField()
    alarm_ack = StringField()
    when = StringField()
    stop_processing: bool = BooleanField(default=False)
    allow_fail: bool = BooleanField(default=False)
    # Approve flag (is user Approved Received Message)
    # Notification adapter for sender
    tt_system: Optional[str] = StringField()
    template: Optional[str] = StringField(required=False)
    # User Actions
    user: Optional[int] = IntField()
    error: Optional[str] = StringField()


class EscalationJob(Document):
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
        "collection": "escalationjobs",
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
    status = EnumField(JobStatus, default=JobStatus.WAIT, required=True)
    # Start escalation timestamp
    created_at = DateTimeField(required=True)
    started_at = DateTimeField(required=False)
    completed_at = DateTimeField(required=False)
    # Escalation context
    ctx_id: int = LongField(required=False)  # Ctx
    telemetry_sample: int = FloatField(default=0)
    end_condition: str = StringField()
    maintenance_policy: str = StringField()
    policy: EscalationGroupPolicy = EnumField(EscalationGroupPolicy, required=True)
    max_repeat: int = IntField(default=0)
    repeat_delay: int = IntField(default=0)
    # Document options
    items: List[EscalationItem] = EmbeddedDocumentListField(EscalationItem)
    actions: List[ActionLog] = EmbeddedDocumentListField(ActionLog)
    # List of group references, if any
    tt_docs = DictField()
    groups = EmbeddedDocumentListField(GroupItem)
    affected_services = ListField(ObjectIdField())
    # affected_maintenances = ListField(ObjectIdField())
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
    def iter_last_for_entities(cls, entities: Iterable[str]) -> Iterable["Job"]:
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
                    #
                    {
                        "$sort": {"entity": 1, "_id": -1},
                    },
                    #
                    {"$group": {"_id": "$entity", "max_id": {"$first": "$_id"}}},
                    #
                    {"$project": {"_id": "$max_id"}},
                ]
            )
        ]
        yield from cls.objects.filter(id__in=ids)
