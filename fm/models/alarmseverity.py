# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmSeverity model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
from itertools import izip
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, UUIDField)
import cachetools
# NOC modules
from noc.main.models.style import Style
from noc.lib.nosql import ForeignKeyField
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json

id_lock = Lock()


class AlarmSeverity(Document):
    """
    Alarm severities
    """
    meta = {
        "collection": "noc.alarmseverities",
        "allow_inheritance": False,
        "indexes": ["severity"],
        "json_collection": "fm.alarmseverities"
    }
    name = StringField(required=True, unique=True)
    uuid = UUIDField(binary=True)
    description = StringField(required=False)
    severity = IntField(required=True)
    style = ForeignKeyField(Style)
    # Minimal alarm weight to reach severity
    min_weight = IntField(required=False)
    sound = StringField(default="alarm")
    volume = IntField(default=100)

    _id_cache = cachetools.TTLCache(maxsize=50, ttl=60)
    _order_cache = {}
    _weight_cache = {}

    def __unicode__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return AlarmSeverity.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_order_cache"), lock=lambda _: id_lock)
    def get_ordered(cls):
        """
        Returns list of severities ordered in acvending order
        :return:
        """
        return list(AlarmSeverity.objects.order_by("severity"))

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_weight_cache"), lock=lambda _: id_lock)
    def get_weights(cls):
        """
        Returns list of (weight, alpha)
        :return:
        """
        sevs = cls.get_ordered()
        weights = [(s.min_weight or 0) for s in sevs]
        severities = [s.severity for s in sevs]
        dw = [float(w1 - w0) for w0, w1 in izip(weights, weights[1:])]
        ds = [float(s1 - s0) for s0, s1 in izip(severities, severities[1:])]
        alpha = [(s / w if w else 0) for s, w in izip(ds, dw)]
        alpha += [alpha[-1]]
        return severities, weights, alpha

    @classmethod
    def get_severity(cls, severity):
        """
        Returns Alarm Severity instance corresponding to numeric value
        """
        for s in reversed(cls.get_ordered()):
            if severity >= s.severity:
                return s
        return s

    @classmethod
    @cachetools.ttl_cache(maxsize=1000, ttl=600)
    def get_severity_css_class_name(cls, severity):
        return cls.get_severity(severity).style.css_class_name

    def get_json_path(self):
        return "%s.json" % quote_safe_path(self.name)

    def to_json(self):
        return to_json({
            "name": self.name,
            "$collection": self._meta["json_collection"],
            "uuid": self.uuid,
            "description": self.description,
            "severity": self.severity,
            "style__name": self.style.name
        }, order=["name", "$collection", "uuid",
                  "description", "severity", "style"])

    @classmethod
    def severity_for_weight(cls, w):
        """
        Calculate absolute severity for given weight *w*
        :returns: severity as int
        """
        def find(weights, w):
            i = 0
            for i, mw in enumerate(weights):
                if w < mw:
                    return max(i - 1, 0)
            return i

        severities, weights, alpha = cls.get_weights()
        i = find(weights, w)
        return severities[i] + int(alpha[i] * (w - weights[i]))
