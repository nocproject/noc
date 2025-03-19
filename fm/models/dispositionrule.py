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
from noc.sa.models.action import Action
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.model.decorator import tree
from noc.core.prettyjson import to_json
from noc.core.text import quote_safe_path
from noc.fm.models.alarmclass import AlarmClass

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
    remote_system: Optional["RemoteSystem"] = ReferenceField(RemoteSystem, required=False)

    def __str__(self):
        return f'{", ".join(self.labels)}'

    @property
    def json_data(self) -> Dict[str, Any]:
        if self.event_class_re:
            return {"event_class_re": self.event_class_re}
        return {}


class AlarmRootCauseCondition(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    alarm_class: AlarmClass = PlainReferenceField(AlarmClass, required=True)
    window = IntField(required=True)
    # Match Object (resource) ?
    topology_rca = BooleanField(default=False)
    affected_service = BooleanField(default=False)
    # affected_resource = BooleanField(default=False)


class ActionItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    # Action API ? by object, move to instance ?
    # Run Diagnostic
    action_command: "Action" = ReferenceField(Action, required=True)
    # run_discovery = BooleanField()
    # Update Resource State
    # TTL


class HandlerItem(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}
    # On Event, On Raise, On Close
    handler: "Handler" = ReferenceField(Handler, required=True)

    @property
    def json_data(self) -> Dict[str, Any]:
        if self.handler:
            return {"handler__name": self.handler.name}
        return {}


@tree(field="replace_rule")
@change
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
    replace_rule: Optional["DispositionRule"] = ReferenceField("self", required=False)
    # Actions
    notification_group: Optional["NotificationGroup"] = ForeignKeyField(
        NotificationGroup, required=False
    )
    subject_template = StringField()
    handlers: List[Handler] = EmbeddedDocumentListField(HandlerItem)
    script_actions: List[ActionItem] = EmbeddedDocumentListField(ActionItem)
    #
    # RCA
    alarm_disposition: Optional["AlarmClass"] = PlainReferenceField(AlarmClass, required=False)
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
    # TTL ?
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

    def iter_changed_datastream(self, changed_fields=None):
        yield "cfgdispositionrules", self.id

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
        if self.combo_condition:
            r |= {
                "combo_condition": self.combo_condition,
                "combo_window": self.combo_window,
                "combo_count": self.combo_count,
            }
        if self.alarm_disposition:
            r["disposition__name"] = self.alarm_disposition.name
        if self.handlers:
            r["handlers"] = [h.json_data for h in self.handlers]
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
                "disposition__name",
                "combo_condition",
                "combo_window",
                "combo_count",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @classmethod
    def get_rule_config(cls, rule: "DispositionRule") -> Dict[str, Any]:
        """Generate Datastream Config"""
        if rule.replace_rule and rule.replace_rule_policy == "w":
            # Merge Rule ?
            return DispositionRule.get_rule_config(rule.replace_rule)
        r = {
            "name": rule.name,
            "is_active": rule.is_active,
            "preference": rule.preference,
            "alarm_class": rule.alarm_disposition.name,
            "stop_processing": rule.stop_processing,
            "action": "processed",
        }
        if rule.notification_group:
            r |= {
                "notification_group": str(rule.notification_group.id),
                "subject_template": rule.subject_template,
            }
        if rule.combo_condition:
            r["combo_condition"] = {
                "combo_condition": rule.combo_condition,
                "combo_window": rule.combo_window,
                "combo_count": rule.combo_count,
            }
        if rule.handlers:
            r["handlers"] = [str(h.id) for h in rule.handlers]
        return r
