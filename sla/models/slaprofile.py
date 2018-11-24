# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SLA Profile models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
# Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, BooleanField, ReferenceField, ListField,
                                EmbeddedDocumentField)
import cachetools
# NOC modules
from noc.main.models.style import Style
from noc.pm.models.metrictype import MetricType
from noc.pm.models.thresholdprofile import ThresholdProfile
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_delete_check

id_lock = Lock()


class SLAProfileMetrics(EmbeddedDocument):
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


@on_delete_check(check=[
    ("sla.SLAProbe", "profile")
])
class SLAProfile(Document):
    """
    SLA profile and settings
    """
    meta = {
        "collection": "noc.sla_profiles",
        "strict": False,
        "auto_create_index": False
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
