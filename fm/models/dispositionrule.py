# ---------------------------------------------------------------------
# Disposition Rule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import operator
from threading import Lock
from typing import Optional, List, Union, Dict, Any

# Third-party modules
from bson import ObjectId
import cachetools
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    ListField,
    LongField,
    IntField,
    UUIDField,
    ReferenceField,
    EmbeddedDocumentListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.handler import Handler
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.action import Action as MOAction
from noc.core.bi.decorator import bi_sync
from noc.core.change.change import on_change
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from .alarmseverity import AlarmSeverity
from .alarmclass import AlarmClass

# from .eventcategory import EventCategory


id_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    # categories: List[EventCategory] = ListField(ReferenceField(EventCategory, required=True))
    # ex_categories: List[EventCategory] = ListField(ReferenceField(EventCategory, required=True))
    event_class_re: str = StringField()
    groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    ex_groups: List[ResourceGroup] = ListField(ReferenceField(ResourceGroup, required=True))
    # severity: AlarmSeverity = ReferenceField(AlarmSeverity, required=False)
    remote_system: AlarmSeverity = ReferenceField(RemoteSystem, required=False)

    def __str__(self):
        return f'{", ".join(self.labels)}'

    @property
    def json_data(self) -> Dict[str, Any]:
        if self.event_class_re:
            return {"event_class_re": self.event_class_re}
        return {}


class AlarmRootCauseCondition(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    alarm_class = PlainReferenceField(AlarmClass, required=True)
    window = IntField(required=True)
    type: str = StringField(choices=["Ar", "Ac"])
    # Match Object (resource) ?
    topology_rca = BooleanField(default=False)
    affected_service = BooleanField(default=False)
    # affected_resource = BooleanField(default=False)


class Action(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    handler = PlainReferenceField(Handler)
    action_command = ReferenceField(MOAction)
    # run_discovery = BooleanField()
    # Update Resource State
    # TTL


@on_change
@bi_sync
class DispositionRule(Document):
    meta = {
        "collection": "dispositionrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.dispositionrules",
        "json_depends_on": ["fm.alarmseverities", "fm.alarmclasses"],
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    description = StringField()
    uuid = UUIDField(binary=True)
    is_active = BooleanField(default=True)
    preference = IntField(required=True, default=1000)
    #
    match: List[Match] = EmbeddedDocumentListField(Match)
    # time_pattern
    # Combo Condition
    combo_condition = StringField(
        required=False,
        default="none",
        choices=[
            (x, x)
            for x in (
                # Apply action immediately
                "none",
                # Apply when event firing rate
                # exceeds combo_count times during combo_window
                "frequency",
                # Apply action if event followed by all combo events
                # in strict order
                "sequence",
                # Apply action if event followed by all combo events
                # in no specific order
                "all",
                # Apply action if event followed by any of combo events
                "any",
                # Only Change !!!!
            )
        ],
    )
    # Time window for combo events in seconds
    combo_window = IntField(required=False, default=0)
    # Applicable for frequency.
    combo_count = IntField(required=False, default=0)
    #
    replace_rule_policy = StringField(
        required=True,
        choices=[
            ("D", "Disable"),
            ("w", "Whole"),
            ("c", "Extend Condition"),
            ("a", "Action"),
        ],
        default="a",
    )
    replace_rule = ReferenceField("self", required=False)
    #
    notification_group = ForeignKeyField(NotificationGroup, required=False)
    subject_template = StringField()
    #
    actions: List[Action] = EmbeddedDocumentListField(Action)
    # RCA
    alarm_disposition = PlainReferenceField(AlarmClass, required=True)
    root_cause = EmbeddedDocumentListField(AlarmRootCauseCondition)
    #
    severity_policy = StringField(
        choices=[
            ("CB", "Class Based Policy"),
            ("AB", "Affected Based Severity Preferred"),
            ("AL", "Affected Limit"),
            ("ST", "By Tokens"),
        ],
        default="AL",
    )
    stop_processing = BooleanField(default=False)
    # TTL
    # BI ID
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_AC_NAME = "Group"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["DispositionRule"]:
        return DispositionRule.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["DispositionRule"]:
        return DispositionRule.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["DispositionRule"]:
        return DispositionRule.objects.filter(bi_id=bi_id).first()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "preference": self.preference,
            "match": [],
            "stop_processing": self.stop_processing,
        }
        if self.match:
            r["match"] = [m.json_data for m in self.match]
        if self.replace_rule:
            r["replace_rule__name"] = self.replace_rule.name
            r["replace_rule_policy"] = self.replace_rule_policy
        if self.disposition:
            r["disposition__name"] = self.disposition.name
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "preference",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    def is_match(self, alarm):
        if not self.match:
            return True
        lset = set(alarm.effective_labels)
        for match in self.match:
            # Match against labels
            if match.exclude_labels and set(match.exclude_labels).issubset(lset):
                continue
            if not set(match.labels).issubset(lset):
                continue
            # Match against alarm class
            if match.alarm_class and match.alarm_class != alarm.alarm_class:
                continue
            # Match severity
            if match.severity and match.severity != AlarmSeverity.get_severity(alarm.severity):
                continue
            return True
