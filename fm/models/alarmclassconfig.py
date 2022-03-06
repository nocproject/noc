# ---------------------------------------------------------------------
# AlarmClassConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, BooleanField, ReferenceField, IntField

# NOC modules
from noc.core.mongo.fields import PlainReferenceField
from noc.pm.models.thresholdprofile import ThresholdProfile
from .alarmclass import AlarmClass


class AlarmClassConfig(Document):
    """
    Alarm class config
    """

    meta = {
        "collection": "noc.fm.alarmclassconfigs",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["alarm_class"],
    }

    alarm_class = PlainReferenceField(AlarmClass, unique=True)
    is_active = BooleanField(default=False)
    description = StringField()
    # Notifiction Delay
    enable_notification_delay = BooleanField(default=False)
    notification_delay = IntField(required=False)
    # Control Time
    enable_control_time = BooleanField(default=False)
    control_time0 = IntField(required=False)
    control_time1 = IntField(required=False)
    control_timeN = IntField(required=False)
    # Alarm Repeat
    enable_alarm_repeat = BooleanField(default=False)
    thresholdprofile = ReferenceField(ThresholdProfile)
    # Alarm close delay
    repeat_alarm_close = IntField(required=False, default=0)

    def __str__(self):
        return self.alarm_class.name
