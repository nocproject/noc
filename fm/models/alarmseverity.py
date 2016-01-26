# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmSeverity model
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, IntField, UUIDField)
import cachetools
## NOC modules
from noc.main.models.style import Style
from noc.lib.nosql import ForeignKeyField
from noc.lib.text import quote_safe_path
from noc.lib.prettyjson import to_json


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

    def __unicode__(self):
        return self.name

    @classmethod
    def get_severity(cls, severity):
        """
        Returns Alarm Severity instance corresponding to numeric value
        """
        s = cls.objects.filter(severity__lte=severity).order_by("-severity").first()
        if not s:
            s = cls.objects.order_by("severity").first()
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
