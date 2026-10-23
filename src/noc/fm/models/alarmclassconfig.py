# ---------------------------------------------------------------------
# AlarmClassConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from .alarmclass import AlarmClass


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
