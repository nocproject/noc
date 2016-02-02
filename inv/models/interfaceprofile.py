## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Interface Profile models
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField,
                                ReferenceField, FloatField, ListField,
                                EmbeddedDocumentField)
## NOC modules
from noc.lib.nosql import ForeignKeyField
from noc.main.models.style import Style
from noc.main.models.notificationgroup import NotificationGroup
from noc.pm.models.metrictype import MetricType


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
    # check_link alarm job interval settings
    # Either None or T0,I0,T1,I1,...,Tn-1,In-1,,In
    # See MultiIntervalJob settings for details
    check_link_interval = StringField(default=",60")
    # Send up/down notifications
    status_change_notification = ForeignKeyField(NotificationGroup,
                                                 required=False)
    # Count as customer port in alarms summary
    is_customer = BooleanField(default=False)
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(InterfaceProfileMetrics))

    def __unicode__(self):
        return self.name

    @classmethod
    def get_default_profile(cls):
        try:
            return cls._default_profile
        except AttributeError:
            cls._default_profile = cls.objects.filter(
                name="default").first()
            return cls._default_profile
