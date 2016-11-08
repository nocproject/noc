# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmSeverity model
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, UUIDField)
import cachetools
## NOC modules
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
    _order_cache = cachetools.TTLCache(maxsize=1, ttl=60)

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

        # Build caches
        if not hasattr(cls, "_weights"):
            cls._weights = []
            cls._severities = []
            cls._alpha = []
            lw = 0
            for i, s in enumerate(AlarmSeverity.objects.order_by("severity")):
                cw = s.min_weight or lw
                lw = w
                cls._weights += [cw]
                cls._severities += [s.severity]
                if i:
                    ds = float(cls._severities[i] - cls._severities[i - 1])
                    dw = float(cls._weights[i] - cls._weights[i - 1])
                    if dw:
                        cls._alpha += [ds / dw]
                    else:
                        cls._alpha += [0]
            if cls._alpha:
                cls._alpha += [cls._alpha[-1]]
        # Calculate severities
        i = find(cls._weights, w)
        return cls._severities[i] + int(cls._alpha[i] * (w - cls._weights[i]))
