## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Profile models
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import RLock
import operator
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField,
                                ReferenceField, FloatField, ListField,
                                EmbeddedDocumentField, IntField)
import cachetools
## NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.main.models.style import Style
from noc.main.models.notificationgroup import NotificationGroup
from noc.pm.models.metrictype import MetricType

id_lock = RLock()


class InterfaceProfileMetrics(EmbeddedDocument):
    metric_type = ReferenceField(MetricType, required=True)
    is_active = BooleanField()
    low_error = FloatField(required=False)
    low_warn = FloatField(required=False)
    high_warn = FloatField(required=False)
    high_error = FloatField(required=False)


class InterfaceProfile(Document):
    """
    Interface SLA profile and settings
    """
    meta = {
        "collection": "noc.interface_profiles",
        "allow_inheritance": False
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
    mac_discovery = BooleanField(default=False)
    # Collect and keep interface status
    status_discovery = BooleanField(default=False)
    # Send up/down notifications
    status_change_notification = ForeignKeyField(NotificationGroup,
                                                 required=False)
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(InterfaceProfileMetrics))
    # Alarm weight
    weight = IntField(default=0)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return InterfaceProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        return InterfaceProfile.objects.filter(name=name).first()

    @classmethod
    def get_default_profile(cls):
        try:
            return cls._default_profile
        except AttributeError:
            cls._default_profile = cls.get_by_name("default")
            return cls._default_profile
