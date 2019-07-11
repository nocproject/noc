# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlarmClassConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from mongoengine.document import Document
from mongoengine.fields import IntField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .alarmclass import AlarmClass


@six.python_2_unicode_compatible
class AlarmClassConfig(Document):
    """
    Alarm class
    """

    meta = {"collection": "noc.alarmclassconfigs", "strict": False, "auto_create_index": False}

    alarm_class = PlainReferenceField(AlarmClass, unique=True)
    notification_delay = IntField(required=False)
    control_time0 = IntField(required=False)
    control_time1 = IntField(required=False)
    control_timeN = IntField(required=False)

    def __str__(self):
        return self.alarm_class.name
