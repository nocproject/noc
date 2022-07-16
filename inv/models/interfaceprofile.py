# ---------------------------------------------------------------------
# Interface Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock, RLock
from typing import Optional, Dict
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
    IntField,
)
from pymongo import ReadPreference
from bson import ObjectId
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.handler import Handler
from noc.main.models.label import Label
from noc.pm.models.metrictype import MetricType
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.cm.models.interfacevalidationpolicy import InterfaceValidationPolicy
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change

from noc.core.model.decorator import on_delete_check
from .ifdescpatterns import IfDescPatterns

id_lock = Lock()
ips_lock = RLock()
metrics_lock = Lock()


@dataclass
class MetricConfig(object):
    metric_type: MetricType
    enable_box: bool
    enable_periodic: bool
    is_stored: bool
    threshold_profile: Optional[ThresholdProfile]


class MatchRule(EmbeddedDocument):
    dynamic_order = IntField(default=0)
    labels = ListField(StringField())
    handler = StringField()

    def __str__(self):
        return f'{self.dynamic_order}: {", ".join(self.labels)}'

    def get_labels(self):
        return list(Label.objects.filter(name__in=self.labels))


class InterfaceProfileMetrics(EmbeddedDocument):
    meta = {"strict": False}
    metric_type = ReferenceField(MetricType, required=True)
    # Metric collection settings
    # Enable during box discovery
    enable_box = BooleanField(default=False)
    # Enable during periodic discovery
    enable_periodic = BooleanField(default=True)
    # Send metrics to persistent store
    is_stored = BooleanField(default=True)
    # Threshold processing
    threshold_profile = ReferenceField(ThresholdProfile)

    def __str__(self):
        return (
            f"{self.metric_type} "
            f"({self.enable_box}/{self.enable_periodic}/{self.is_stored}):"
            f' {self.threshold_profile.name if self.threshold_profile else ""}'
        )


@bi_sync
@change
@on_delete_check(
    check=[
        ("inv.Interface", "profile"),
        ("inv.InterfaceClassificationRule", "profile"),
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
    #
    allow_lag_mismatch = BooleanField(default=False)
    # Send up/down notifications
    status_change_notification = ForeignKeyField(NotificationGroup, required=False)
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(InterfaceProfileMetrics))
    # Alarm weight
    weight = IntField(default=0)
    # User network interface
    # MAC discovery can be restricted to UNI
    is_uni = BooleanField(default=False)
    # Allow automatic segmentation
    allow_autosegmentation = BooleanField(default=False)
    # Allow collecting metrics from subinterfaces
    allow_subinterface_metrics = BooleanField(default=False)
    #
    allow_vacuum_bulling = BooleanField(default=False)
    # Validation policy
    interface_validation_policy = PlainReferenceField(InterfaceValidationPolicy)
    #
    ifdesc_patterns = PlainReferenceField(IfDescPatterns)
    ifdesc_handler = PlainReferenceField(Handler)
    # Enable abduct detection on interface
    enable_abduct_detection = BooleanField(default=False)
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

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _status_discovery_cache = cachetools.TTLCache(maxsize=10, ttl=120)
    _interface_profile_metrics = cachetools.TTLCache(maxsize=1000, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id) -> Optional["InterfaceProfile"]:
        return InterfaceProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id) -> Optional["InterfaceProfile"]:
        return InterfaceProfile.objects.filter(bi_id=id).first()

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
    def config_from_settings(m: "InterfaceProfileMetrics") -> "MetricConfig":
        """
        Returns MetricConfig from .metrics field
        :param m:
        :return:
        """
        return MetricConfig(
            m.metric_type, m.enable_box, m.enable_periodic, m.is_stored, m.threshold_profile
        )

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
            r[m.metric_type.name] = cls.config_from_settings(m)
        return r
