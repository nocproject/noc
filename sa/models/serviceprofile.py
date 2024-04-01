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
from typing import Optional, Union, Tuple, List, Dict
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
    alarm_var = StringField()


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
        if self.status and status > self.status:
            return False
        if self.op and self.weight and weight < self.weight:
            return False
        return True


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
    severity = PlainReferenceField(AlarmSeverity)  # Min Severity
    # weight = IntField()
    status = EnumField(Status, required=True)


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
    status_transfer_function = StringField(
        choices=[
            ("P", "By percent count"),
            ("MIN", "Minimal on all Children"),
            ("MAX", "Maximum on all children"),
            # ("W", "Weight Sum Condition"),
        ],
        default="MIN",
    )
    # For Wight and Percent
    status_transfer_rule: List[StatusTransferRule] = EmbeddedDocumentListField(StatusTransferRule)
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

    def calculate_status(self, services: List[Tuple[Status, int]]) -> Status:
        if self.status_transfer_function == "MIN":
            return min(svc for svc, weigh in services)
        elif self.status_transfer_function == "MAX":
            return max(svc for svc, weigh in services)
        return Status.UP

    @classmethod
    def get_alarm_service_filter(cls):
        ...


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
