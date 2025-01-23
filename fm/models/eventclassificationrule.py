# ---------------------------------------------------------------------
# EventClassificationRule model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
from typing import Iterable, List, Dict, Any, Tuple

# Third-party modules
from mongoengine.fields import (
    StringField,
    IntField,
    ListField,
    DictField,
    ObjectIdField,
    UUIDField,
    EmbeddedDocumentListField,
    EnumField,
    ReferenceField,
    BooleanField,
)
from mongoengine.document import EmbeddedDocument, Document

# NOC modules
from .eventclass import EventClass
from noc.fm.models.mib import MIB
from noc.fm.models.enumeration import Enumeration
from noc.sa.models.profile import GENERIC_PROFILE, Profile
from noc.core.fm.event import Event, MessageType, EventSource, Target
from noc.core.mongo.fields import PlainReferenceField
from noc.core.escape import fm_unescape
from noc.core.text import quote_safe_path
from noc.core.prettyjson import to_json


class EventClassificationRuleVar(EmbeddedDocument):
    meta = {"strict": False}
    name = StringField(required=True)
    convert = StringField(
        choices=[
            ("ifindex", "Resolve ifindex"),
            ("enum", "Enum"),
            ("bin_mac", "Binary to MAC"),
        ],
        required=False,
    )
    enum = PlainReferenceField(Enumeration)
    value = StringField(required=False)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    @property
    def json_data(self):
        return {"name": self.name, "value": self.value}


class EventClassificationRuleLabel(EmbeddedDocument):
    meta = {"strict": False}
    wildcard = StringField(required=True)
    is_required = BooleanField(default=True)
    # set_label = StringField(required=False)
    # rewrite_label
    set_var = StringField()

    def __str__(self):
        if self.is_required:
            return f"{self.wildcard} (required)"
        return self.wildcard

    @property
    def json_data(self):
        r = {"wildcard": self.wildcard, "is_required": self.is_required}
        if self.set_var:
            r["set_var"] = self.set_var
        return r


class EventClassificationRuleCategory(Document):
    meta = {
        "collection": "noc.eventclassificationrulecategories",
        "strict": False,
        "auto_create_index": False,
    }
    name = StringField()
    parent = ObjectIdField(required=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if " | " in self.name:
            p_name = " | ".join(self.name.split(" | ")[:-1])
            p = EventClassificationRuleCategory.objects.filter(name=p_name).first()
            if not p:
                p = EventClassificationRuleCategory(name=p_name)
                p.save()
            self.parent = p.id
        else:
            self.parent = None
        super().save(*args, **kwargs)


class EventClassificationPattern(EmbeddedDocument):
    meta = {"strict": False}
    key_re = StringField(required=True)
    value_re = StringField(required=True)

    def __str__(self):
        return "'%s' : '%s'" % (self.key_re, self.value_re)

    def __eq__(self, other):
        return self.key_re == other.key_re and self.value_re == other.value_re

    @property
    def json_data(self):
        return {
            "key_re": self.key_re,
            "value_re": self.value_re,
        }


class EventClassificationTestCase(EmbeddedDocument):
    meta = {"strict": False}
    message = StringField()
    raw_vars = ListField(DictField())
    input_labels = ListField(StringField())

    @property
    def json_data(self):
        r = {
            "message": self.message,
            "raw_vars": self.raw_vars,
        }
        if self.input_labels:
            r["input_labels"] = list(self.input_labels)
        return r


class EventClassificationRule(Document):
    """
    Classification rules
    """

    meta = {
        "collection": "noc.eventclassificationrules",
        "strict": False,
        "auto_create_index": False,
        "json_collection": "fm.eventclassificationrules",
        "json_depends_on": ["fm.eventclasses"],
        "json_unique_fields": ["name"],
    }
    name = StringField(required=True, unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    event_class: EventClass = PlainReferenceField(EventClass, required=True)
    preference = IntField(required=True, default=1000)
    patterns: List[EventClassificationPattern] = EmbeddedDocumentListField(
        EventClassificationPattern
    )
    sources: List[EventSource] = ListField(
        EnumField(EventSource), default=lambda: [EventSource.OTHER]
    )
    profiles: List[Profile] = ListField(ReferenceField(Profile))
    message_rx: str = StringField()
    # datasources = EmbeddedDocumentListField(DataSource)
    vars: List[EventClassificationRuleVar] = EmbeddedDocumentListField(EventClassificationRuleVar)
    labels: List[EventClassificationRuleLabel] = EmbeddedDocumentListField(
        EventClassificationRuleLabel
    )
    test_cases: List[EventClassificationTestCase] = EmbeddedDocumentListField(
        EventClassificationTestCase
    )
    #
    category = ObjectIdField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        c_name = " | ".join(self.name.split(" | ")[:-1])
        c = EventClassificationRuleCategory.objects.filter(name=c_name).first()
        if not c:
            c = EventClassificationRuleCategory(name=c_name)
            c.save()
        self.category = c.id
        super().save(*args, **kwargs)

    @property
    def short_name(self):
        return self.name.split(" | ")[-1]

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "event_class__name": self.event_class.name,
            "preference": self.preference,
            "sources": [s.value for s in self.sources],
            "patterns": [p.json_data for p in self.patterns],
            "labels": [ll.json_data for ll in self.labels],
        }
        if self.message_rx:
            r["message_rx"] = self.message_rx
        if self.profiles:
            r["profiles"] = [mt.name for mt in self.profiles]
        if self.description:
            r["description"] = self.description
        if self.vars:
            r["vars"] = [s.json_data for s in self.vars]
        if self.test_cases:
            r["test_cases"] = [t.json_data for t in self.test_cases]
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "event_class__name",
                "preference",
                "sources",
                "vars",
                "patterns",
            ],
        )

    def get_json_path(self) -> str:
        p = [quote_safe_path(n.strip()) for n in self.name.split("|")]
        return os.path.join(*p) + ".json"

    @staticmethod
    def resolve_vars(data: List[Dict[str, Any]]) -> Dict[str, Any]:
        r = {}
        snmp_vars = {}
        for d in data:
            if d.get("snmp_raw"):
                snmp_vars[d["name"]] = fm_unescape(d["value"])
            else:
                r[d["name"]] = d["value"]
        if snmp_vars:
            r.update(MIB.resolve_vars(snmp_vars))
        return r

    def iter_cases(self) -> Iterable[Tuple[Event, Dict[str, Any]]]:
        ts = 0
        mt = MessageType(profile=GENERIC_PROFILE, source=self.sources[0])
        if self.profiles:
            mt.profile = self.profiles[0].name
        for p in self.patterns:
            if p.key_re == "^source$" or p.key_re == "source":
                mt.source = EventSource(p.value_re.strip("^$"))
            if p.key_re == "^profile$" or p.key_re == "profile":
                mt.profile = p.value_re.strip("^$").replace("\\", "")
        for tc in self.test_cases:
            yield Event(
                ts=ts + 1,
                target=Target(address="10.10.10.10", name="test", id="10"),
                data=[],
                type=mt,
                message=tc.message,
                labels=tc.input_labels if tc.input_labels else None,
            ), self.resolve_vars(tc.raw_vars)
