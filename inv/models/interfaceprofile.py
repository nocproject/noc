# ---------------------------------------------------------------------
# Interface Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock, RLock
from typing import Optional, Dict, Union, Callable, Any, Tuple
from dataclasses import dataclass
import operator

# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    BooleanField,
    LongField,
    ReferenceField,
    ListField,
    EmbeddedDocumentField,
    ObjectIdField,
    IntField,
)
from pymongo import ReadPreference
from bson import ObjectId
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.handler import Handler
from noc.main.models.label import Label
from noc.main.models.notificationgroup import NotificationGroup
from noc.pm.models.metrictype import MetricType
from noc.cm.models.interfacevalidationpolicy import InterfaceValidationPolicy
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.model.decorator import on_delete_check, on_init
from noc.core.matcher import build_matcher
from noc.wf.models.workflow import Workflow
from noc.config import config
from .ifdescpatterns import IfDescPatterns

id_lock = Lock()
ips_lock = RLock()
metrics_lock = Lock()

NON_DISABLED_METRIC_TYPE = {"Interface | Status | Oper", "Interface | Status | Admin"}


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    is_stored: bool
    interval: int


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    resource_groups = ListField(ObjectIdField())
    # untagged_vlan_filter: VLANFilter = PlainReferenceField(VLANFilter, required=False)
    # tagged_vlan_filter: VLANFilter = PlainReferenceField(VLANFilter, required=False)
    # prefix_filter = ForeignKeyField(PrefixTable, required=False)
    # name_patter = StringField()
    # description_patter = StringField()

    def get_match_expr(self) -> Dict[str, Any]:
        r = {}
        if self.labels:
            r["labels"] = {"$all": list(self.labels)}
        if self.resource_groups:
            r["service_groups"] = {"$all": [str(x) for x in self.resource_groups]}
        # if self.untagged_vlan_filter:
        #     r["untagged_vlan"] = {"$in": self.untagged_vlan_filter.include_vlans}
        # if self.tagged_vlan_filter:
        #     r["tagged_vlans"] = {"$any": self.tagged_vlan_filter.include_vlans}
        # if self.name_patter:
        #     r["name"] = {"$regex": self.name_patter}
        # if self.description_patter:
        #     r["description"] = {"$regex": self.description_patter}
        return r

    def __str__(self):
        return f'{self.dynamic_order}: {", ".join(self.labels)}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class InterfaceProfileMetrics(EmbeddedDocument):
    meta = {"strict": False}
    metric_type = ReferenceField(MetricType, required=True)
    # Metric collection settings
    # Send metrics to persistent store
    is_stored = BooleanField(default=True)
    # Interval for collecter metrics
    interval = IntField(min_value=0)

    def __str__(self):
        return self.metric_type.name


@Label.match_labels("interface_profile", allowed_op={"="})
@bi_sync
@on_init
@change(audit=True)
@on_delete_check(
    check=[
        ("inv.Interface", "profile"),
        ("inv.SubInterface", "profile"),
        ("sa.ServiceProfile", "interface_profile"),
    ]
)
class InterfaceProfile(Document):
    """
    Interface SLA profile and settings
    """

    meta = {
        "collection": "noc.interface_profiles",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "match_rules.labels",
            "status_discovery",
            ("match_rules.dynamic_order", "match_rules.labels"),
            ("dynamic_classification_policy", "match_rules.labels"),
        ],
    }
    name = StringField(unique=True)
    description = StringField()
    style = ForeignKeyField(Style, required=False)
    workflow = PlainReferenceField(Workflow)
    # Interface-level events processing
    link_events = StringField(
        required=True,
        choices=[
            ("I", "Ignore Events"),
            ("L", "Log events, do not raise alarms"),
            ("A", "Raise alarms"),
        ],
        default="A",
    )
    # Discovery settings
    discovery_policy = StringField(
        choices=[("I", "Ignore"), ("O", "Create new"), ("R", "Replace"), ("C", "Add to cloud")],
        default="R",
    )
    # Collect mac addresses on interface
    mac_discovery_policy = StringField(
        choices=[
            ("d", "Disabled"),
            ("m", "Management VLAN"),
            ("e", "Transit"),
            ("i", "Direct Downlink"),
            ("c", "Chained Downlink"),
            ("u", "Direct Uplink"),
            ("C", "Cloud Downlink"),
        ],
        default="d",
    )
    # Collect and keep interface status
    status_discovery = StringField(
        choices=[
            ("d", "Disabled"),
            ("e", "Enable"),
            ("c", "Clear Alarm"),
            ("ca", "Clear Alarm if Admin Down"),
            ("rc", "Raise & Clear Alarm"),
        ],
        default="d",
    )
    metric_collected_policy = StringField(
        choices=[
            ("e", "Enable"),
            ("da", "Disable if Admin Down"),
            ("do", "Disable if Oper Down"),
        ],
        default="e",
    )
    #
    allow_lag_mismatch = BooleanField(default=False)
    # Send up/down notifications
    status_change_notification = StringField(
        choices=[
            ("d", "Disabled"),
            ("e", "Enable Message"),
        ],
        default="d",
    )
    default_notification_group = ForeignKeyField(NotificationGroup, required=False)
    #
    metrics_default_interval = IntField(default=0, min_value=0)
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(InterfaceProfileMetrics))
    # Alarm weight
    weight = IntField(default=0)
    # User network interface
    # MAC discovery can be restricted to UNI
    is_uni = BooleanField(default=False)
    # Allow automatic segmentation
    allow_autosegmentation = BooleanField(default=False)
    #
    allow_vacuum_bulling = BooleanField(default=False)
    # Validation policy
    interface_validation_policy = PlainReferenceField(InterfaceValidationPolicy)
    #
    ifdesc_patterns = PlainReferenceField(IfDescPatterns)
    ifdesc_handler = PlainReferenceField(Handler)
    # Enable abduct detection on interface
    enable_abduct_detection = BooleanField(default=False)
    #
    subinterface_apply_policy = StringField(
        choices=[
            ("I", "Inherit from Interface"),
            ("R", "By Rule"),
            ("D", "Disable (Interface Only)"),
        ],
        default="D",
    )
    # Dynamic Profile Classification
    dynamic_classification_policy = StringField(
        choices=[("R", "By Rule"), ("D", "Disable")],
        default="R",
    )
    #
    match_rules = ListField(EmbeddedDocumentField(MatchRule))
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
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _status_discovery_cache = cachetools.TTLCache(maxsize=10, ttl=120)
    _interface_profile_metrics = cachetools.TTLCache(maxsize=1000, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def iter_changed_datastream(self, changed_fields=None):
        from noc.inv.models.interface import Interface

        if not config.datastream.enable_cfgmetricsources:
            return
        if (
            changed_fields
            and "metrics_default_interval" not in changed_fields
            and "metrics" not in changed_fields
        ):
            return
        mos = {
            mo.bi_id
            for mo in Interface.objects.filter(
                profile=self, type__in=["physical", "aggregated"]
            ).scalar("managed_object")
        }
        for bi_id in mos:
            yield "cfgmetricsources", f"sa.ManagedObject::{bi_id}"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["InterfaceProfile"]:
        return InterfaceProfile.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, bi_id: int) -> Optional["InterfaceProfile"]:
        return InterfaceProfile.objects.filter(bi_id=bi_id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name) -> Optional["InterfaceProfile"]:
        return InterfaceProfile.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls) -> "InterfaceProfile":
        return InterfaceProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_status_discovery_cache"), lock=lambda _: ips_lock
    )
    def get_with_status_discovery(cls):
        """
        Get list of interface profile ids with status_discovery = True
        :return:
        """
        return list(
            x["_id"]
            for x in InterfaceProfile._get_collection()
            .with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
            .find({"status_discovery": {"$ne": "d"}}, {"_id": 1})
        )

    @staticmethod
    def config_from_settings(
        m: "InterfaceProfileMetrics", profile_interval: Optional[int] = None
    ) -> "MetricConfig":
        """
        Returns MetricConfig from .metrics field
        :param m:
        :param profile_interval:
        :return:
        """
        return MetricConfig(m.metric_type, m.is_stored, m.interval or profile_interval)

    @classmethod
    @cachetools.cachedmethod(
        operator.attrgetter("_interface_profile_metrics"), lock=lambda _: metrics_lock
    )
    def get_interface_profile_metrics(cls, p_id: ObjectId) -> Dict[str, MetricConfig]:
        r = {}
        ipr = InterfaceProfile.get_by_id(id=p_id)
        if not ipr:
            return r
        for m in ipr.metrics:
            r[m.metric_type.name] = cls.config_from_settings(m, ipr.metrics_default_interval)
        return r

    @property
    def is_enabled_notification(self) -> bool:
        return self.status_change_notification != "d"

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_interface")

    @classmethod
    def iter_lazy_labels(cls, interface_profile: "InterfaceProfile"):
        yield f"noc::interface_profile::{interface_profile.name}::="

    @property
    def allow_subinterface_metrics(self):
        return self.subinterface_apply_policy != "D" and self.metrics

    def allow_collected_metric(
        self,
        admin_status: Optional[bool],
        oper_status: Optional[bool],
        metric_type: Optional[str] = None,
    ) -> bool:
        """
        Check metric collected policy by interface status
        :param admin_status:
        :param oper_status:
        :param metric_type:
        :return:
        """
        if self.status_discovery == "d" or self.metric_collected_policy == "e":
            return True
        if metric_type and metric_type in NON_DISABLED_METRIC_TYPE:
            # Not disabled metric
            return True
        if self.metric_collected_policy == "da" and admin_status is False:
            return False
        if self.metric_collected_policy == "do" and oper_status is False:
            return False
        return True

    def get_matcher(self) -> Callable:
        """"""
        expr = []
        for r in self.match_rules:
            expr.append(r.get_match_expr())
        if len(expr) == 1:
            return build_matcher(expr[0])
        return build_matcher({"$or": expr})

    def is_match(self, o) -> bool:
        """Local Match rules"""
        matcher = self.get_matcher()
        ctx = o.get_matcher_ctx()
        return matcher(ctx)

    @classmethod
    def get_profiles_matcher(cls, subinterface: bool = False) -> Tuple[Tuple[str, Callable], ...]:
        """Build matcher based on Profile Match Rules"""
        r = {}
        if subinterface:
            profiles = InterfaceProfile.objects.filter(subinterface_apply_policy="R")
        else:
            profiles = InterfaceProfile.objects.filter(dynamic_classification_policy__ne="D")
        for ip in profiles:
            for mr in ip.match_rules:
                r[(str(ip.id), mr.dynamic_order)] = build_matcher(mr.get_match_expr())
        return tuple((x[0], r[x]) for x in sorted(r, key=lambda i: i[1]))
