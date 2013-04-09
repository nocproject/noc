# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlarmSeverity model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.lib.nosql as nosql
from noc.main.models.style import Style


class AlarmSeverity(nosql.Document):
    """
    Alarm severities
    """
    meta = {
        "collection": "noc.alarmseverities",
        "allow_inheritance": False
    }
    name = nosql.StringField(required=True, unique=True)
    is_builtin = nosql.BooleanField(default=False)
    description = nosql.StringField(required=False)
    severity = nosql.IntField(required=True)
    style = nosql.ForeignKeyField(Style)

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
