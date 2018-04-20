# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AlarmClassConfig model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField
# NOC modules
=======
##----------------------------------------------------------------------
## AlarmClassConfig model
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.nosql import PlainReferenceField
from alarmclass import AlarmClass


class AlarmClassConfig(Document):
    """
    Alarm class
    """
    meta = {
        "collection": "noc.alarmclassconfigs",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False
=======
        "allow_inheritance": False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    }

    alarm_class = PlainReferenceField(AlarmClass, unique=True)
    notification_delay = IntField(required=False)
    control_time0 = IntField(required=False)
    control_time1 = IntField(required=False)
    control_timeN = IntField(required=False)

    def __unicode__(self):
        return self.alarm_class.name
