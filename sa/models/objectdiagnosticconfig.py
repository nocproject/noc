# ---------------------------------------------------------------------
# DiagnosticConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Dict, Any


# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    UUIDField,
    BooleanField,
    ListField,
    EmbeddedDocumentListField,
    ReferenceField,
    LongField,
    IntField,
)
from mongoengine.queryset.base import NULLIFY
import cachetools

# NOC modules
from noc.core.model.decorator import tree
from noc.core.bi.decorator import bi_sync
from noc.core.prettyjson import to_json
from noc.fm.models.alarmclass import AlarmClass

id_lock = Lock()


class RunConfig(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    enable_box = BooleanField(default=False)
    enable_periodic = BooleanField(default=False)
    enable_manual = BooleanField(default=True)
    save_history = BooleanField(default=True)
    run_policy = StringField(choices=["F", "A"], default="A")
    run_order = StringField(choices=["S", "E"], default="S")  # On start, On End


class DiagnosticCheck(EmbeddedDocument):
    check = StringField(required=True)
    arg0 = StringField()

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"check": self.check}
        if self.arg0:
            r["arg0"] = self.arg0
        return r


@bi_sync
@tree(field="diagnostics")
class ObjectDiagnosticConfig(Document):
    meta = {
        "collection": "objectdiagnosticconfigs",
        "strict": False,
        "auto_create_index": False,
        "indexes": [],
        "json_collection": "sa.objectdiagnosticconfigs",
        "json_unique_fields": ["name"],
    }

    name = StringField(unique=True)
    uuid = UUIDField(binary=True)
    description = StringField()
    # Display settings
    show_in_display = BooleanField(default=True)
    display_order = IntField(default=900)
    #
    # saved_result = BooleanField(default=False)
    #
    state_policy = StringField(choices=["ALL", "ANY"], default="ANY")
    checks = EmbeddedDocumentListField(DiagnosticCheck)
    diagnostics = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))
    # Alarm Settings
    alarm_class = ReferenceField(AlarmClass)
    alarm_labels = ListField(StringField())
    # Running Settings
    runs = EmbeddedDocumentListField(RunConfig)
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid) -> Optional["ObjectDiagnosticConfig"]:
        return ObjectDiagnosticConfig.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, oid) -> Optional["ObjectDiagnosticConfig"]:
        return ObjectDiagnosticConfig.objects.filter(bi_id=oid).first()

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
                "policy",
                "show_in_info",
                "checks",
                "diagnostics",
            ],
        )
