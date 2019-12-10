# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator

# Third-party modules
import six
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
import cachetools

# NOC modules
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.main.models.style import Style
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.remotesystem import RemoteSystem
from noc.pm.models.metrictype import MetricType
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.cm.models.interfacevalidationpolicy import InterfaceValidationPolicy
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


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


@bi_sync
@on_delete_check(
    check=[
        ("inv.Interface", "profile"),
        ("inv.InterfaceClassificationRule", "profile"),
        ("inv.SubInterface", "profile")
        # ("sa.ServiceProfile", "")
    ]
)
@six.python_2_unicode_compatible
class InterfaceProfile(Document):
    """
    Interface SLA profile and settings
    """

    meta = {"collection": "noc.interface_profiles", "strict": False, "auto_create_index": False}
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
    status_discovery = BooleanField(default=False)
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
    # Validation policy
    interface_validation_policy = PlainReferenceField(InterfaceValidationPolicy)
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
    _status_discovery_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return InterfaceProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return InterfaceProfile.objects.filter(bi_id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return InterfaceProfile.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls):
        return InterfaceProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_status_discovery_cache"), lock=lambda _: id_lock)
    def get_with_status_discovery(cls):
        """
        Get list of interface profile ids with status_discovery = True
        :return:
        """
        return list(
            x["_id"]
            for x in InterfaceProfile._get_collection().find({"status_discovery": True}, {"_id": 1})
        )
