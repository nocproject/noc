# ---------------------------------------------------------------------
# DiagnosticConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Dict, Any, Iterable, List


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
from noc.core.wf.diagnostic import DiagnosticConfig
from noc.core.checkers.base import Check
from noc.fm.models.alarmclass import AlarmClass
from noc.main.models.label import Label

id_lock = Lock()


class Match(EmbeddedDocument):
    labels = ListField(StringField())
    exclude_labels = ListField(StringField())

    def __str__(self):
        return f'{", ".join(self.labels)}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


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
    checks: List[DiagnosticCheck] = EmbeddedDocumentListField(DiagnosticCheck)
    diagnostics = ListField(ReferenceField("self", reverse_delete_rule=NULLIFY))
    # Alarm Settings
    alarm_class = ReferenceField(AlarmClass)
    alarm_labels = ListField(StringField())
    # Running Settings
    match = EmbeddedDocumentListField(Match)
    # Run Settings
    enable_box = BooleanField(default=False)
    enable_periodic = BooleanField(default=False)
    enable_manual = BooleanField(default=True)
    #
    save_history = BooleanField(default=True)
    run_policy = StringField(choices=["F", "A"], default="A")
    run_order = StringField(choices=["S", "E"], default="S")  # On start, On End
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

    def get_diagnostic_config(self) -> "DiagnosticConfig":

        return DiagnosticConfig(
            diagnostic=self.name,
            checks=[Check(name=c.name, arg0=c.arg0) for c in self.checks],
            dependent=self.diagnostics,
            state_policy=self.state_policy,
            run_policy=self.run_policy,
            run_order=self.run_order,
            discovery_box=self.enable_box,
            discovery_periodic=self.enable_periodic,
            save_history=self.save_history,
            show_in_display=self.show_in_display,
            display_order=self.display_order,
            alarm_class=self.alarm_class,
            alarm_labels=self.alarm_labels,
        )

    @classmethod
    def iter_object_diagnostics(cls, object) -> Iterable[DiagnosticConfig]:
        """
        Iter over Diagnostic Config for object
        First - diagnostic with checks only
        Second - Diagnostic with Dependency
        :param object:
        :return:
        """
        deferred = list()
        for odc in ObjectDiagnosticConfig.objects.filter(match__labels__in=object.effective_labels):
            dc = odc.get_diagnostic_config()
            if odc.dependent:
                deferred.append(dc)
                continue
            yield dc
        for dc in deferred:
            yield dc
