# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SLA Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, BooleanField, FloatField, ReferenceField, ListField,
    EmbeddedDocumentField, IntField)
import cachetools
# NOC modules
from noc.main.models.style import Style
from noc.pm.models.metrictype import MetricType
from noc.lib.nosql import ForeignKeyField

id_lock = Lock()


class SLAProfileMetrics(EmbeddedDocument):
    metric_type = ReferenceField(MetricType, required=True)
    # Collect metric
    is_active = BooleanField()
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
    window_function = StringField(
        choices=[
            # Call handler
            # window_config is a handler
            ("handler", "Handler"),
            # Last measure
            ("last", "Last Value"),
            # Average, no config
            ("avg", "Average"),
            # Percentile, window_config is in a percent
            ("percentile", "Percentile"),
            # 25% percentile
            ("q1", "1st Quartile"),
            # 50% percentile, median
            ("q2", "2st Quartile"),
            # 75% percentile
            ("q3", "3st Quartile"),
            # 95% percentile
            ("p95", "95% percentile"),
            # 99% percentile
            ("p99", "99% percentile")
        ],
        default="last"
    )
    # Window function configuration
    window_config = StringField()
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


class SLAProfile(Document):
    """
    SLA profile and settings
    """
    meta = {
        "collection": "noc.sla_profiles",
        "allow_inheritance": False
    }
    name = StringField(unique=True)
    description = StringField()
    #
    style = ForeignKeyField(Style, required=False)
    # Interface profile metrics
    metrics = ListField(EmbeddedDocumentField(SLAProfileMetrics))

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return SLAProfile.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name):
        try:
            return SLAProfile.objects.get(name=name)
        except SLAProfile.DoesNotExist:
            return None
