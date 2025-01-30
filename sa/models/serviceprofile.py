# ----------------------------------------------------------------------
# Service Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import re
import enum
from threading import Lock
from typing import Optional, Union, Tuple, List
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
from mongoengine.queryset.visitor import Q as m_q
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
from noc.core.models.serviceinstances import Status, InstanceType
from noc.fm.models.alarmclass import AlarmClass
from noc.inv.models.capability import Capability
from noc.wf.models.workflow import Workflow
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change


id_lock = Lock()


class CapsSettings(EmbeddedDocument):
    capability = ReferenceField(Capability)
    default_value = DynamicField()
    allowed_manual = BooleanField(default=False)


condition_map = {
    "=": lambda s, w: s == w,
    ">=": lambda s, w: s >= w,
    "<=": lambda s, w: s <= w,
}


class InstancePolicySettings(EmbeddedDocument):
    """
    Rules for Resource to Instance map.
    Attributes:
        # type:
        #     * AS Service - on local instance
        #     * AS Client - create binding instance
        type: global_id/resources
            * L2 (MAC) - interface, vlan
            * L3 (IP + Port ? pool) - interface, subinterface, vlan
            * OS Process (ManagedObject + Pid|Name) - L3
            * Chanel - Interface, BGP Peer

        only_one_object: Instance only one object (if more - replace)
        allow_manual: Allow manual binding instance
        send_approve: Send Resource Approve if bind to Instance   # Reserved ?
        allow_resources: Resource Codes Allowed to bind
        allow_dynamic_register: Allow automatically update address/port
    """

    # provide = StringField(choices=[("C", "AS Client"), ("S", "AS Service")], default="S")
    instance_type = EnumField(InstanceType, default=InstanceType.OTHER)
    allow_manual: bool = BooleanField(default=False)
    only_one_object = BooleanField(default=True)  # Allow bind multiple resources
    allow_resources: List[str] = ListField(
        StringField(choices=[("si", "SubInterface"), ("if", "Interface")])
    )
    send_approve: bool = BooleanField(default=False)
    # allow_dynamic_register: bool  = BooleanField(default=False)
    # Update Instance Status from resource
    # update_status = BooleanField(default=False)


class CalculatedStatusRule(EmbeddedDocument):
    """
    Calculate status rule
    1. Input - List[Tuple[Status, <weight>]]
    2. Filter input list by min/max status
    3. Filtered weights - calculate weights
    4. Compare calculate value with condition
    5. if match - return set_status
    6. Without match - return
    """

    weight_function = StringField(
        choices=[
            ("C", "Count"),
            ("CP", "Percent"),
            ("MIN", "Minimal"),
            ("MAX", "Maximum"),
        ]
    )
    op = StringField(choices=["=", ">=", "<="], default="=")
    weight = IntField(min_value=0)
    # Value
    # Capabilities, check int Type
    min_status = EnumField(Status)
    max_status = EnumField(Status)
    # For instance ?
    set_status = EnumField(Status, required=True)

    def get_status(self, statuses: List[Tuple[Status, int]]) -> Optional[Status]:
        weights = (w for s, w in statuses if self.is_match_status(s))
        weight = self.calculate_weight(weights)
        if condition_map[self.op](weight, self.weight):
            return self.set_status
        return None

    # calculate_status - statuses - List[(status, weight)]

    def is_match_status(self, status: Status) -> bool:
        if not self.min_status and status < self.min_status:
            return False
        elif self.max_status and status >= self.max_status:
            return False
        return True

    def is_match(self, status: Status, weight: int) -> bool:
        if not self.min_status and status < self.min_status:
            return False
        elif self.max_status and status >= self.max_status:
            return False
        if self.weight:
            return condition_map[self.op](weight, self.weight)
        return True

    def calculate_weight(self, weights: Tuple[int, ...]) -> float:
        if self.weight_function == "C":
            return len(weights)
        elif self.weight_function == "MIN":
            return min(weights)
        elif self.weight_function == "MAX":
            return max(weights)
        # filter by min/max status
        return round(sum(weights) / len(weights) * 100, 2)

    # def get_status(
    #     self, severities: List[int], max_services: Optional[int] = None
    # ) -> Optional[AlarmSeverity]:
    #     severity = 0
    #     if self.transfer_function == "max":
    #         severity = max(severities)
    #     elif self.transfer_function == "min":
    #         severity = min(severities)
    #     elif self.transfer_function == "percent" and self.percent:
    #         c = Counter(sorted(severities, reverse=True))
    #         r = 0
    #         r_max = max_services or sum(c.values())
    #         for s, count in c.items():
    #             r += count
    #             if (r / r_max) * 100 >= self.percent:
    #                 if not self.severity:
    #                     severity = s
    #                     break
    #                 if self.severity and AlarmSeverity.get_severity(s) >= self.severity:
    #                     severity = s
    #                     break
    #     if not severity:
    #         return None
    #     return self.status


class AlarmStatusRule(EmbeddedDocument):
    """
    Mapping Alarm to Service Status
    Attributes:
        alarm_class_template: Condition by Alarm Class Name Regex
        min_severity: Minimum Alarm Severity for match
        max_severity: Maximum Alarm Severity for match
        status: Set Service Status
    """

    alarm_class_template: Optional[str] = StringField(required=False)
    include_labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    affected_instance = BooleanField(default=False)  # Include ServiceInstance to
    min_severity: Optional["AlarmSeverity"] = PlainReferenceField(AlarmSeverity)  # Min Severity
    max_severity: Optional["AlarmSeverity"] = PlainReferenceField(AlarmSeverity)  # Max Severity
    # set_weight
    status = EnumField(Status, required=False)  # Default status by Severity

    def is_match(self, alarm) -> bool:
        """"""
        if self.min_severity and alarm.severity < self.min_severity.severity:
            return False
        if self.max_severity and alarm.severity > self.max_severity.severity:
            return False
        if self.alarm_class_template:
            return bool(re.match(self.alarm_class_template, alarm.alarm_class.name))
        if self.include_labels and set(self.include_labels) - set(alarm.effective_labels):
            return False
        return True


@Label.match_labels("serviceprofile", allowed_op={"="})
@Label.model
@bi_sync
@change
@on_save
@on_delete_check(
    check=[("sa.Service", "profile")],
    clean_lazy_labels="serviceprofile",
)
class ServiceProfile(Document):
    """
    Attributes:
        status_transfer_policy: Configure Transfer status to dependencies
            * D - Disable Status Transfer
            * T - Transfer received status, without changes
            * S - transfer self Status
    """

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
    # Status Policies
    status_transfer_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("T", "Transparent"),
            ("S", "Self"),
        ],
        default="S",
    )
    # From Parent
    parent_status_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("T", "Transparent"),
            ("R", "By Rule"),
        ],
        default="T",
    )
    calculate_status_function = StringField(
        choices=[
            ("D", "Disable"),
            ("MX", "Max status"),
            ("MN", "Min status"),
            ("R", "By Rule"),
        ],
        default="MX",
    )
    calculate_status_rule: List["CalculatedStatusRule"] = EmbeddedDocumentListField(
        CalculatedStatusRule
    )
    # Alarm Binding
    alarm_affected_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("A", "By Instance"),
            ("O", "By Filter"),
        ],
        default="D",
    )
    alarm_status_rules: List["AlarmStatusRule"] = EmbeddedDocumentListField(AlarmStatusRule)
    raise_status_alarm_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("R", "Root Only"),
            ("O", "Always"),
        ],
        default="R",
    )
    # Instance Resources
    instance_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("N", "Resource Binding"),
            ("O", "Allow Register"),
        ],
        default="N",
    )
    instance_policy_settings: "InstancePolicySettings" = EmbeddedDocumentField(
        InstancePolicySettings
    )
    # Capabilities
    caps = EmbeddedDocumentListField(CapsSettings)
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
    _alarm_rule_cache = cachetools.TTLCache(50, ttl=120)

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

    @classmethod
    def get_status_by_severity(cls, severity: int) -> Status:
        """Calculate Status by Alarm Severity"""
        for num, s in enumerate(AlarmSeverity.objects.filter().order_by("-severity")):
            if num > 3:
                break
            status = Status(4 - num)
            if s.severity <= severity and status > Status.SLIGHTLY_DEGRADED:
                return status
        return Status.UNKNOWN

    def get_resource_policy(self, type: str = "service"):
        """
        Return resource binding policy
        Attrs:
            type: service, client
        """

    def calculate_alarm_status(self, aa) -> Status:
        """
        Calculate Alarm status by rule
        Attrs:
            aa: Active Alarm Instance
        """
        if not self.alarm_status_rules:
            return self.get_status_by_severity(aa.severity)
        for r in self.alarm_status_rules:
            if not r.is_match(aa):
                continue
            if r.status:
                return r.status
            return self.get_status_by_severity(aa.severity)
        return Status.UNKNOWN

    def get_alarm_service_filter(self):
        r = m_q()
        for rule in self.alarm_status_rules:
            q = m_q()
            if rule.alarm_class_template:
                ac = list(
                    AlarmClass.objects.filter(name=re.compile(rule.alarm_class_template)).scalar(
                        "id"
                    )
                )
                if not ac:
                    continue
                q &= m_q(alarm_class__in=ac)
            if rule.include_labels:
                q &= m_q(effective_labels__in=rule.include_labels)
            if rule.min_severity:
                q &= m_q(severity__gte=rule.min_severity)
            if rule.max_severity:
                q &= m_q(severity__lte=rule.max_severity)
            if q:
                r |= q
        return r

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_alarm_rule_cache"), lock=lambda _: id_lock)
    def get_alarm_rules(cls) -> List[Tuple[str, Optional[Tuple[AlarmStatusRule, ...]]]]:
        """"""
        r = []
        for p in ServiceProfile.objects.filter(alarm_affected_policy__ne="D"):
            if p.alarm_affected_policy == "A":
                r.append((p.id, None))
                continue
            r.append((p.id, tuple(p.alarm_status_rules)))
        return r


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
