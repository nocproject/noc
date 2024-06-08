# ----------------------------------------------------------------------
# Service Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from enum import IntEnum
from threading import Lock
from typing import Optional, Union, Tuple, List
from collections import Counter
from functools import partial

# Third-party modules
from bson import ObjectId
from pymongo import UpdateOne
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ReferenceField,
    IntField,
    BooleanField,
    LongField,
    ListField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    DynamicField,
    EnumField,
)
import cachetools

# NOC modules
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_save
from noc.core.bi.decorator import bi_sync
from noc.core.defer import defer
from noc.core.hash import hash_int
from noc.inv.models.capability import Capability
from noc.wf.models.workflow import Workflow
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change


id_lock = Lock()


class Status(IntEnum):
    UNKNOWN = 0
    UP = 1
    SLIGHTLY_DEGRADED = 2
    DEGRADED = 3
    DOWN = 4


class CapsSettings(EmbeddedDocument):
    capability = ReferenceField(Capability)
    default_value = DynamicField()
    allowed_manual = BooleanField(default=False)


condition_map = {
    "=": lambda s, w: s == w,
    ">=": lambda s, w: s >= w,
    "<=": lambda s, w: s <= w,
}


class StatusTransferRule(EmbeddedDocument):
    service_profile = PlainReferenceField("sa.ServiceProfile", required=False)
    op = StringField(choices=["=", ">=", "<="], default="=")
    status = EnumField(Status, required=False)
    weight = IntField(min_value=0)
    ignore = BooleanField(default=False)
    to_status = EnumField(Status, required=True)

    def is_match(
        self,
        profile: Optional[str] = None,
        status: Optional[Status] = None,
        weight: Optional[int] = None,
    ) -> bool:
        if self.service_profile and profile != self.service_profile:
            return False
        if self.status and status == self.status:
            return False
        if self.op and self.weight and weight < self.weight:
            return False
        return True


class StatusMapRule(EmbeddedDocument):
    op = StringField(choices=["=", ">=", "<="], default="=")
    weight = IntField(min_value=0)
    status = EnumField(Status)
    to_status = EnumField(Status, required=True)

    def is_match(self, status, weight) -> bool:
        if not self.status and not self.weight:
            return self.to_status
        if not self.status:
            return condition_map[self.op](weight, self.weight)
        if not self.weight:
            return condition_map[self.op](status, self.status)
        return condition_map[self.op](status, self.status) and condition_map[self.op](
            weight, self.weight
        )


class AlarmFilter(EmbeddedDocument):
    alarm_class = PlainReferenceField(AlarmSeverity)
    include_labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    include_object = BooleanField(default=False)  # Include ManagedObject to filter
    # resource_group
    # Vars ?


class AlarmStatusMap(EmbeddedDocument):
    # alarm_class = PlainReferenceField(AlarmClass)  # Name RE
    transfer_function = StringField(choices=["min", "max", "percent", "sum"])  # Handler ?
    op = StringField(choices=["<=", ">=", "="])
    percent = IntField(min_value=0)
    severity = PlainReferenceField(AlarmSeverity)  # Min Severity
    # weight = IntField()
    status = EnumField(Status, required=True)

    def get_status(
        self, severities: List[int], max_services: Optional[int] = None
    ) -> Optional[AlarmSeverity]:
        severity = 0
        if self.transfer_function == "max":
            severity = max(severities)
        elif self.transfer_function == "min":
            severity = min(severities)
        elif self.transfer_function == "percent" and self.percent:
            c = Counter(sorted(severities, reverse=True))
            r = 0
            r_max = max_services or sum(c.values())
            for s, count in c.items():
                r += count
                if (r / r_max) * 100 >= self.percent:
                    if not self.severity:
                        severity = s
                        break
                    if self.severity and AlarmSeverity.get_severity(s) >= self.severity:
                        severity = s
                        break
        if not severity:
            return None
        return self.status


@Label.match_labels("serviceprofile", allowed_op={"="})
@Label.model
@bi_sync
@change
@on_save
@on_delete_check(check=[("sa.Service", "profile")], clean_lazy_labels="serviceprofile")
class ServiceProfile(Document):
    meta = {
        "collection": "noc.serviceprofiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["labels"],
    }
    name = StringField(unique=True)
    description = StringField()
    # Jinja2 service label template
    card_title_template = StringField()
    # Short service code for reporting
    code = StringField()
    # FontAwesome glyph
    glyph = StringField()
    # Glyph order in summary
    display_order = IntField(default=100)
    # Show in total summary
    show_in_summary = BooleanField(default=True)
    workflow: Workflow = PlainReferenceField(
        Workflow, default=partial(Workflow.get_default_workflow, "sa.ServiceProfile")
    )
    # Auto-assign interface profile when service binds to interface
    interface_profile: "InterfaceProfile" = ReferenceField(InterfaceProfile)
    # Alarm weight
    weight: int = IntField(default=0)
    #
    status_transfer_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("T", "Transparent"),
            ("R", "By Rule"),
        ],
        default="T",
    )
    # For Wight and Percent
    status_transfer_rule: List[StatusTransferRule] = EmbeddedDocumentListField(StatusTransferRule)
    status_transfer_function = StringField(
        choices=[
            ("P", "By percent count"),
            ("MIN", "Minimal on all Children"),
            ("MAX", "Maximum on all children"),
            ("SUM", "Sum Weight"),
        ],
        default="MIN",
    )
    status_transfer_map: List[StatusMapRule] = EmbeddedDocumentListField(StatusMapRule)
    # Alarm Binding
    alarm_affected_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("A", "Any"),
            ("O", "By Filter"),
        ],
        default="D",
    )
    alarm_filter: List["AlarmFilter"] = EmbeddedDocumentListField(AlarmFilter)
    alarm_status_map: List["AlarmStatusMap"] = EmbeddedDocumentListField(AlarmStatusMap)
    # Capabilities
    caps = ListField(EmbeddedDocumentField(CapsSettings))
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)
    # Labels
    labels = ListField(StringField())

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Service Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ServiceProfile"]:
        return ServiceProfile.objects.filter(id=oid).first()

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "interface_profile" in self._changed_fields:
            defer(
                "noc.sa.models.serviceprofile.refresh_interface_profiles",
                key=hash_int(self.id),
                sp_id=str(self.id),
                ip_id=str(self.interface_profile.id) if self.interface_profile else None,
            )

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, "enable_serviceprofile")

    @classmethod
    def iter_lazy_labels(cls, service_profile: "ServiceProfile"):
        yield f"noc::serviceprofile::{service_profile.name}::="

    def calculate_status(self, statuses: List[Tuple[Status, int]]) -> Status:
        if not statuses:
            return Status.UNKNOWN
        status = (status for status, _ in statuses)
        weight = (weight for _, weight in statuses)
        if self.status_transfer_function == "MIN":
            status = min(status)
            weight = min(weight)
        elif self.status_transfer_function == "MAX":
            status = max(status)
            weight = max(weight)
        elif self.status_transfer_function == "SUM":
            weight = sum(weight for status, weight in statuses if status == Status.DOWN)
            status = sum(status)
        if not self.status_transfer_map:
            return status
        for rule in self.status_transfer_map:
            if rule.is_match(status, weight):
                return rule.to_status
        return Status.UNKNOWN

    def calculate_alarm_status(self, severities, max_object: Optional[int] = None) -> Status:
        """

        :param severities: List of alarms severities
        :param max_object: Max objects that may be alarmed
        :return:
        """
        if not severities:
            return Status.UP
        if not self.alarm_status_map:
            # Default behaviour
            alarm_sev = AlarmSeverity.get_severity(max(severities))
            for num, s in enumerate(AlarmSeverity.objects.filter().order_by("-severity")):
                if num > 3:
                    break
                status = Status(4 - num)
                if s == alarm_sev and status > Status.SLIGHTLY_DEGRADED:
                    return status
                else:
                    break
        for rule in self.alarm_status_map:
            s = rule.get_status(severities, max_services=max_object)
            if s:
                return rule.status
        return Status.UP

    @classmethod
    def get_alarm_service_filter(cls): ...


def refresh_interface_profiles(sp_id, ip_id):
    from .service import Service
    from noc.inv.models.interface import Interface

    svc = [x["_id"] for x in Service._get_collection().find({"profile": sp_id}, {"_id": 1})]
    if not svc:
        return
    collection = Interface._get_collection()
    bulk = []
    bulk += [UpdateOne({"_id": {"$in": svc}}, {"$set": {"profile": ip_id}})]
    collection.bulk_write(bulk, ordered=False)
