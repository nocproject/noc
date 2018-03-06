# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Interface Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, LongField,
                                ReferenceField, FloatField, ListField,
                                EmbeddedDocumentField, IntField)
import cachetools
# NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.main.models.style import Style
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.remotesystem import RemoteSystem
from noc.pm.models.metrictype import MetricType
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.core.bi.decorator import bi_sync
from noc.core.model.decorator import on_delete_check
from noc.core.window import wf_choices

id_lock = Lock()


class InterfaceProfileMetrics(EmbeddedDocument):
    metric_type = ReferenceField(MetricType, required=True)
    # Metric collection settings
    # Enable during box discovery
    enable_box = BooleanField(default=False)
    # Enable during periodic discovery
    enable_periodic = BooleanField(default=True)
    # Send metrics to persistent store
    is_stored = BooleanField(default=True)
    # Window depth
    window_type = StringField(
        max_length=1,
        choices=[
            ("m", "Measurements"),
            ("t", "Time")
        ]
    )
    # Window size. Depends on window type
    # * m - amount of measurements
    # * t - time in seconds
    window = IntField(default=1)
    # Window function
    # Accepts window as a list of [(timestamp, value)]
    # and window_config
    # and returns float value
    window_function = StringField(choices=wf_choices, default="last")
    # Window function configuration
    window_config = StringField()
    # Convert window function result to percents of interface bandwidth
    window_related = BooleanField(default=False)
    # Threshold settings
    # Raise error if window_function result is below *low_error*
    low_error = FloatField(required=False)
    # Raise warning if window_function result is below *low_warn*
    low_warn = FloatField(required=False)
    # Raise warning if window_function result is above *high_warn*
    high_warn = FloatField(required=False)
    # Raise error if window_function result is above *high_err*
    high_error = FloatField(required=False)
    # Severity weights
    low_error_weight = IntField(default=10)
    low_warn_weight = IntField(default=1)
    high_warn_weight = IntField(default=1)
    high_error_weight = IntField(default=10)
    # Threshold processing
    threshold_profile = ReferenceField(ThresholdProfile)


@bi_sync
@on_delete_check(check=[
    ("inv.Interface", "profile"),
    ("inv.InterfaceClassificationRule", "profile"),
    ("inv.SubInterface", "profile")
    # ("sa.ServiceProfile", "")
])
class InterfaceProfile(Document):
    """
    Interface SLA profile and settings
    """
    meta = {
        "collection": "noc.interface_profiles",
        "strict": False,
        "auto_create_index": False
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
            ("A", "Raise alarms")
        ],
        default="A"
    )
    # Discovery settings
    discovery_policy = StringField(
        choices=[
            ("I", "Ignore"),
            ("O", "Create new"),
            ("R", "Replace"),
            ("C", "Add to cloud")
        ],
        default="R"
    )
    # Collect mac addresses on interface
    mac_discovery_policy = StringField(
        choices=[
            ("d", "Disabled"),
            ("m", "Management VLAN"),
            ("e", "Enabled")
        ],
        default="d"
    )
    # Collect and keep interface status
    status_discovery = BooleanField(default=False)
    #
    allow_lag_mismatch = BooleanField(default=False)
    # Send up/down notifications
    status_change_notification = ForeignKeyField(NotificationGroup,
                                                 required=False)
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
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = ReferenceField(RemoteSystem)
    # Object id in remote system
    remote_id = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _default_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    DEFAULT_PROFILE_NAME = "default"

    def __unicode__(self):
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
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return InterfaceProfile.objects.filter(name=name).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_default_cache"), lock=lambda _: id_lock)
    def get_default_profile(cls):
        return InterfaceProfile.objects.filter(name=cls.DEFAULT_PROFILE_NAME).first()
