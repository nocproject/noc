# ---------------------------------------------------------------------
# Escalation model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BinaryField,
    DateTimeField,
    ListField,
    EmbeddedDocumentListField,
    ObjectIdField,
)
from typing import List, Set

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from .escalationprofile import EscalationProfile


class EscalationItem(EmbeddedDocument):
    meta = {"strict": False}
    managed_object = ForeignKeyField(ManagedObject)
    alarm = ObjectIdField()
    escalation_status = StringField(
        choices=["new", "maintenance", "exists", "ok", "temp", "fail"], default="new"
    )
    escalation_error = StringField()
    deescalation_status = StringField(
        choices=["active", "skip", "ok", "temp", "fail", "reescalated"], default="active"
    )
    deescalation_error = StringField()
    # Link to existent escalation, when escalation status is EXISTS
    current_escalation = ObjectIdField()
    current_tt_id = StringField()

    def __str__(self) -> str:
        return f"{self.managed_object.name}:{self.alarm}"

    @property
    def is_new(self) -> bool:
        """
        Check if item is new (no escalation attempts)
        """
        return self.escalation_status == "new"

    @property
    def is_already_escalated(self) -> bool:
        """
        Check if item is already escalated
        """
        return self.escalation_status == "exists"

    @property
    def is_maintenance(self) -> bool:
        """
        Check if item is under maintenance
        """
        return self.escalation_status == "maintenance"


class Escalation(Document):
    meta = {
        "collection": "escalations",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["items.alarm", "close_timestamp", "items.0.alarm"],
    }
    profile = PlainReferenceField(EscalationProfile)
    timestamp = DateTimeField()
    close_timestamp = DateTimeField()
    # tt_system = PlainReferenceField(TTSystem)
    tt_id = StringField()
    prev_escalation = ObjectIdField()
    items = EmbeddedDocumentListField(EscalationItem)
    # List of group references, if any
    groups = ListField(BinaryField())
    # Escalation summary
    total_objects = EmbeddedDocumentListField(ObjectSummaryItem)
    total_services = EmbeddedDocumentListField(SummaryItem)
    total_subscribers = EmbeddedDocumentListField(SummaryItem)

    def __str__(self) -> str:
        return str(self.id)

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
        return self.items[0]

    @property
    def consequences(self) -> List[EscalationItem]:
        return self.items[1:]
