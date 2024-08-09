# ---------------------------------------------------------------------
# DiagnosticConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
from threading import Lock
from typing import Optional, Dict, Any, Iterable, List, Union


# Third-party modules
from bson import ObjectId
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
from mongoengine.errors import ValidationError
import cachetools

# NOC modules
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

    def is_match(self, labels: List[str]):
        if self.exclude_labels and not set(self.exclude_labels) - set(labels):
            return False
        if not set(self.labels) - set(labels):
            return True
        return False


class DiagnosticCheck(EmbeddedDocument):
    check = StringField(required=True)
    script = StringField(required=False)
    arg0 = StringField()

    def __str__(self):
        return f"{self.check}:{self.arg0}"

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {"check": self.check}
        if self.arg0:
            r["arg0"] = self.arg0
        if self.script:
            r["script"] = self.script
        return r


@bi_sync
class ObjectDiagnosticConfig(Document):
    meta = {
        "collection": "objectdiagnosticconfigs",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["match.labels", "match.exclude_labels"],
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _active_diagnostic_cache = cachetools.TTLCache(maxsize=10, ttl=600)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ObjectDiagnosticConfig"]:
        return ObjectDiagnosticConfig.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["ObjectDiagnosticConfig"]:
        return ObjectDiagnosticConfig.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_active_diagnostic_cache"), lock=lambda _: id_lock
    )
    def get_active_diagnostics(cls) -> List["ObjectDiagnosticConfig"]:
        return list(ObjectDiagnosticConfig.objects.filter())

    def is_allowed(self, labels: List[str]) -> bool:
        """
        Check transition allowed
        :param labels:
        :return:
        """
        if not self.match:
            return True
        for match in self.match:
            if match.is_match(labels):
                return True
        return False

    def clean(self):
        if self in self.diagnostics:
            raise ValidationError({"diagnostics": "Same diagnostic in depend check not allowed"})

    @property
    def json_data(self) -> Dict[str, Any]:
        r = {
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            #
            "show_in_display": self.show_in_display,
            "display_order": self.display_order,
            #
            "state_policy": self.state_policy,
            "checks": [c.json_data for c in self.checks],
            #
            "save_history": self.save_history,
            "enable_box": self.enable_box,
            "enable_periodic": self.enable_periodic,
            "enable_manual": self.enable_manual,
            "run_policy": self.run_policy,
            "run_order": self.run_order,
        }
        if self.alarm_class:
            r["alarm_class__name"] = self.alarm_class.name
        return r

    def to_json(self) -> str:
        return to_json(
            self.json_data,
            order=[
                "name",
                "$collection",
                "uuid",
                "description",
            ],
        )

    def get_json_path(self) -> str:
        return f"{self.name}.json"

    @property
    def d_config(self) -> "DiagnosticConfig":
        return DiagnosticConfig(
            diagnostic=self.name,
            checks=[
                Check(name=c.check, args={"arg0": c.arg0}, script=c.script) for c in self.checks
            ],
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
        for odc in cls.get_active_diagnostics():
            if not odc.is_allowed(labels=getattr(object, "effective_labels", [])):
                continue
            dc = odc.d_config
            if odc.diagnostics:
                deferred.append(dc)
                continue
            yield dc
        for dc in deferred:
            yield dc
