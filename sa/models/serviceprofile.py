# ----------------------------------------------------------------------
# Service Profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
import re
from collections import defaultdict
from threading import Lock
from typing import Optional, Union, Tuple, List, Dict, Type, Iterable
from functools import partial

# Third-party modules
import cachetools
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
    EmbeddedDocumentListField,
    EnumField,
)
from mongoengine.queryset.visitor import Q as m_q

# NOC modules
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.core.mongo.fields import PlainReferenceField
from noc.core.model.decorator import on_save
from noc.core.bi.decorator import bi_sync
from noc.core.defer import defer
from noc.core.hash import hash_int
from noc.core.models.servicestatus import Status
from noc.core.models.serviceinstanceconfig import (
    InstanceType,
    ServiceInstanceConfig,
    ServiceInstanceTypeConfig,
)
from noc.core.model.decorator import on_delete_check
from noc.core.change.decorator import change
from noc.core.caps.types import CapsConfig
from noc.core.diagnostic.types import DiagnosticConfig, CtxItem
from noc.main.models.handler import Handler
from noc.inv.models.capability import Capability
from noc.inv.models.resourcegroup import ResourceGroup
from noc.sa.models.capsprofile import CapsProfile
from noc.wf.models.workflow import Workflow
from noc.fm.models.alarmseverity import AlarmSeverity
from noc.fm.models.alarmclass import AlarmClass

id_lock = Lock()


class DiagnosticSettings(EmbeddedDocument):
    meta = {"strict": False, "auto_create_index": False}

    diagnostic: str = StringField(required=True)
    # from_instance_checks
    show_in_display = BooleanField(default=True)
    state_policy = StringField(choices=["ALL", "ANY"], default="ANY")
    # check_handler
    handler: "Handler" = ReferenceField(Handler, required=False)
    instance_checks = BooleanField(default=False)
    ctx: str = ListField(StringField(required=True))
    alarm_class: Optional["AlarmClass"] = ReferenceField(AlarmClass, required=False)
    alarm_subject: str = StringField(max_length=256, required=False)
    # For instance ?
    failed_status = EnumField(Status, required=False)

    def clean(self):
        super().clean()
        if self.handler and not self.handler.allow_diagnostics_checks:
            raise ValueError("Only Diagnostic Checks handler allowed")
        # Validate Ctx
        if self.ctx:
            for c in self.ctx:
                CtxItem.from_string(c)

    def get_config(self, checks=None) -> DiagnosticConfig:
        return DiagnosticConfig(
            diagnostic=self.diagnostic,
            show_in_display=self.show_in_display,
            state_policy=self.state_policy,
            diagnostic_handler=self.handler.handler if self.handler else None,
            diagnostic_ctx=[CtxItem.from_string(c) for c in self.ctx or []],
            check_discovery_policy="L",
        )


condition_map = {
    "=": lambda s, w: s == w,
    ">=": lambda s, w: s >= w,
    "<=": lambda s, w: s <= w,
}


class InstanceSettings(EmbeddedDocument):
    """
    Rules for Resource to Instance map.
    Attributes:
        # type:
        #     * AS Service - on local instance
        #     * AS Client - create binding instance
        instance_type: global_id/resources
            * L2 (MAC) - interface, vlan
            * L3 (IP + Port ? pool) - interface, subinterface, vlan
            * OS Process (ManagedObject + Pid|Name) - L3
            * Chanel - Interface, BGP Peer

        only_one_instance: Instance only one object (if more - replace)
        allow_manual: Allow manual binding instance
        send_approve: Send Resource Approve if bind to Instance   # Reserved ?
        allow_resources: Resource Codes Allowed to bind
        allow_register: Allow register instance for Discovery
        ttl: Time to remove instance without sources
    """

    meta = {"strict": False, "auto_create_index": False}

    # provide = StringField(choices=[("C", "AS Client"), ("S", "AS Service")], default="S")
    instance_type: InstanceType = EnumField(InstanceType, default=InstanceType.OTHER, required=True)
    allow_manual: bool = BooleanField(default=False)
    only_one_instance = BooleanField(default=True)  # Allow bind multiple resources
    allow_resources: List[str] = ListField(
        StringField(choices=[("si", "SubInterface"), ("if", "Interface")])
    )
    send_approve: bool = BooleanField(default=False)
    allow_register: bool = BooleanField(default=False)
    asset_group: bool = PlainReferenceField(ResourceGroup, required=False)
    network_type: str = StringField(
        choices=[
            ("A", "Access"),
            ("P", "Peer"),
            ("E", "Enhanced"),
        ]
    )
    ttl: int = IntField(min_value=0, default=0)
    refs_caps: Capability = ReferenceField(Capability)
    name: str = StringField(required=False)
    # Weight for calculate Alarm
    weight: int = IntField(default=0)
    checks: List[str] = ListField(StringField())
    # Update Instance Status from resource
    # update_status = BooleanField(default=False)

    def __str__(self):
        if self.refs_caps:
            return f"{self.instance_type} ({self.refs_caps.name}): {self.name}"
        return f"{self.instance_type}: {self.name}"

    def get_config(self) -> "ServiceInstanceTypeConfig":
        return ServiceInstanceTypeConfig(
            allow_manual=self.allow_manual,
            only_one_instance=self.only_one_instance,
            allow_resources=self.allow_resources,
            send_approve=self.send_approve,
            allow_register=self.allow_register,
            ttl=self.ttl,
            refs_caps=self.refs_caps,
        )

    def get_instance_type(self) -> Type["ServiceInstanceConfig"]:
        return ServiceInstanceConfig.get_type(self.instance_type)


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

    meta = {"strict": False, "auto_create_index": False}

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

    def __str__(self):
        if self.weight:
            s = f" {self.op} {self.weight} -> {self.set_status.name}"
        else:
            s = f" {self.op} -> {self.set_status.name}"
        if self.min_status or self.max_status:
            return f"({self.min_status} <> {self.max_status}) {s}"
        return s

    def get_status(self, statuses: Dict[Status, int]) -> Optional[Status]:
        weights = tuple(w for s, w in statuses.items() if self.is_match_status(s))
        if not weights:
            return None
        if not self.weight:
            return self.set_status
        weight = self.calculate_weight(weights, max_weight=sum(w for s, w in statuses.items()))
        if condition_map[self.op](weight, self.weight):
            return self.set_status
        return None

    # calculate_status - statuses - List[(status, weight)]

    def is_match_status(self, status: Status) -> bool:
        if self.min_status and status < self.min_status:
            return False
        return not (self.max_status and status >= self.max_status)

    def is_match(self, status: Status, weight: int) -> bool:
        if not self.min_status and status < self.min_status:
            return False
        if self.max_status and status >= self.max_status:
            return False
        if self.weight:
            return condition_map[self.op](weight, self.weight)
        return True

    def calculate_weight(self, weights: Tuple[int, ...], max_weight=1) -> float:
        if self.weight_function == "C":
            return len(weights)
        if self.weight_function == "MIN":
            return min(weights)
        if self.weight_function == "MAX":
            return max(weights)
        if self.weight_function == "CP":
            # filter by min/max status
            return round(sum(weights) / max_weight * 100, 2)
        return round(sum(weights) / len(weights), 2)

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
    allow_partial: bool = BooleanField(default=False)
    include_labels = ListField(StringField())
    exclude_labels = ListField(StringField())
    affected_instance = BooleanField(default=False)  # Include ServiceInstance to
    min_severity: Optional["AlarmSeverity"] = PlainReferenceField(AlarmSeverity)  # Min Severity
    max_severity: Optional["AlarmSeverity"] = PlainReferenceField(AlarmSeverity)  # Max Severity
    # set_weight
    status = EnumField(Status, required=False)  # Default status by Severity

    def __str__(self):
        return f"{self.alarm_class_template or 'ANY'} (AF:{self.affected_instance})"

    def is_match(self, alarm) -> bool:
        """"""
        if self.min_severity and alarm.severity < self.min_severity.severity:
            return False
        if self.max_severity and alarm.severity > self.max_severity.severity:
            return False
        if self.allow_partial and self.alarm_class_template:
            return bool(re.match(self.alarm_class_template, alarm.alarm_class.name))
        if self.alarm_class_template:
            return self.alarm_class_template == alarm.alarm_class.name
        return not (self.include_labels and set(self.include_labels) - set(alarm.effective_labels))


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
    calculate_status_rules: List["CalculatedStatusRule"] = EmbeddedDocumentListField(
        CalculatedStatusRule
    )
    # Alarm Binding
    alarm_affected_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("B", "By Object"),
            ("A", "By Instance"),
            ("O", "By Filter"),
        ],
        default="D",
    )
    alarm_status_rules: List["AlarmStatusRule"] = EmbeddedDocumentListField(AlarmStatusRule)
    raise_status_alarm_policy = StringField(
        choices=[
            ("D", "Disable"),
            ("R", "Group"),
            ("A", "Direct"),
        ],
        default="R",
    )
    alarm_subject_template: Optional[str] = StringField(required=False)
    raise_alarm_class = ReferenceField(AlarmClass)
    include_root_group = BooleanField(default=False)
    # Instance Resources
    # Default Config
    instance_policy = StringField(
        choices=[
            ("D", "Disable"),  # Disabled
            ("A", "Any"),
            ("C", "From Config"),  # By Settings
            # ("G", "By Group"),  # By Settings
            # ("N", "Resource Binding"),
            # ("O", "Allow Register"),
        ],
        default="A",
    )
    instance_settings: List["InstanceSettings"] = EmbeddedDocumentListField(
        InstanceSettings, required=False
    )
    # Send up/down notifications
    status_change_notification = StringField(
        choices=[
            ("d", "Disabled"),
            ("e", "Enable Message"),
        ],
        default="d",
    )
    # Diagnostics status
    diagnostic_status: List[DiagnosticSettings] = EmbeddedDocumentListField(DiagnosticSettings)
    # Capabilities
    caps_profile: Optional[CapsProfile] = ReferenceField(CapsProfile, required=False)
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
    _code_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _alarm_rule_cache = cachetools.TTLCache(50, ttl=120)

    DEFAULT_PROFILE_NAME = "default"
    DEFAULT_WORKFLOW_NAME = "Service Default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["ServiceProfile"]:
        return ServiceProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_code_cache"), lock=lambda _: id_lock)
    def get_by_code(cls, code: str) -> Optional["ServiceProfile"]:
        return ServiceProfile.objects.filter(code=code).first()

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
            if s.severity <= severity and status >= Status.SLIGHTLY_DEGRADED:
                return status
        return Status.UNKNOWN

    def get_caps_config(self) -> Dict[str, CapsConfig]:
        """Local Capabilities Config (from Profile)"""
        r = {}
        if not self.caps_profile:
            return r
        for c in self.caps_profile.caps:
            r[str(c.capability.id)] = c.get_config()
        return r

    def get_instance_config(
        self, i_type: InstanceType, name: Optional[str] = None
    ) -> Optional["ServiceInstanceTypeConfig"]:
        """Getting instance Config"""
        if self.instance_policy == "A":
            cfg = ServiceInstanceTypeConfig()
        else:
            cfg = None
        # Check policy
        for s in self.instance_settings:
            if s.instance_type != i_type:
                continue
            if name and name.endswith("@") and not s.name:
                cfg = s.get_config()
                break
            if name and s.name and name.endswith(s.name):
                cfg = s.get_config()
                break
            if not name and not s.name:
                cfg = s.get_config()
        return cfg

    @property
    def is_enabled_notification(self) -> bool:
        return self.status_change_notification != "d"

    def get_resource_policy(self, type: str = "service"):
        """
        Return resource binding policy
        Attrs:
            type: service, client
        """

    def get_rule_by_alarm(self, aa) -> Optional["AlarmStatusRule"]:
        for r in self.alarm_status_rules:
            if r.is_match(aa):
                return r
        # if self.alarm_affected_policy == "B" or self.alarm_affected_policy == "I":
        #    return AlarmStatusRule(affected_instance=True)
        return None

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

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_alarm_rule_cache"), lock=lambda _: id_lock)
    def get_alarm_rules(cls) -> List[Tuple[str, Optional[Tuple[AlarmStatusRule, ...]], str]]:
        """"""
        r = []
        for p in ServiceProfile.objects.filter(alarm_affected_policy__ne="D"):
            if p.alarm_affected_policy != "O":
                r.append((p.id, None, p.alarm_affected_policy))
            else:
                r.append((p.id, tuple(p.alarm_status_rules), p.alarm_affected_policy))
        return r

    @classmethod
    def get_alarm_service_filter(cls, alarm) -> List[Tuple[m_q, List[str]]]:
        """Getting alarm filter by ServiceProfile rules"""
        from noc.sa.models.serviceinstance import ServiceInstance

        r = defaultdict(list)
        queries = {}
        for pid, rules, policy in ServiceProfile.get_alarm_rules():
            if rules is None:
                q = ServiceInstance.get_instance_filter_by_alarm(
                    alarm, include_object=policy == "B"
                )
                if q:
                    queries[str(q)] = q
                    r[str(q)] += [pid]
            if not rules:
                continue
            q = m_q()
            for rule in rules:
                if not rule.is_match(alarm):
                    continue
                if rule.affected_instance:
                    q |= ServiceInstance.get_instance_filter_by_alarm(alarm, include_object=True)
                else:
                    # Without instance rule
                    r[None] += [pid]
            if q:
                queries[str(q)] = q
                r[str(q)] += [pid]
        return [(queries[x] if x else x, r[x]) for x in r]

    def iter_configured_instances(self) -> List["ServiceInstanceConfig"]:
        """Get configuration"""
        for settings in self.instance_settings:
            yield settings.get_instance_type()

    def iter_diagnostic_configs(self, svc) -> Iterable[DiagnosticConfig]:
        """Iterate over configured diagnostic"""
        for s in self.diagnostic_status or []:
            yield s.get_config()


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
