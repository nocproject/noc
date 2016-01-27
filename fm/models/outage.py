# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Outage report
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.nosql import (Document, IntField, DateTimeField,
                           BooleanField)


class Outage(Document):
    meta = {
        "collection": "noc.fm.outages",
        "allow_inheritance": False,
        "indexes": ["object", "start"]
    }

    object = IntField()
    start = DateTimeField()
    stop = DateTimeField()  # None for active outages

    def __unicode__(self):
        return u"%d" % self.object

    @property
    def is_active(self):
        return self.stop is None

    @classmethod
    def register_outage(cls, object, status, ts=None):
        """
        Change current outage status
        :param cls:
        :param object: Managed Object
        :param status: True - if object is down, False - otherwise
        :param ts: Effective event timestamp. None for current time
        :return:
        """
        ts = ts or datetime.datetime.now()
        o = cls.objects.filter(object=object.id,
            start__lte=datetime.datetime.now()).order_by("-start").first()
        if o and o.is_active and not status:
            # Close active outage
            o.stop = ts
            o.save()
        elif status and ((o and not o.is_active) or not o):
            # Create new outage
            Outage(object=object.id, start=ts, stop=None).save()
