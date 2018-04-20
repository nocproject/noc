# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Outage report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, DateTimeField
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Outage(Document):
    meta = {
        "collection": "noc.fm.outages",
<<<<<<< HEAD
        "strict": False,
        "auto_create_index": False,
        "indexes": ["object", ("object", "-start")]
=======
        "allow_inheritance": False,
        "indexes": ["object", "start"]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    def register_outage(cls, object, status, ts=None):
=======
    def register_outage(cls, object, status):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        """
        Change current outage status
        :param cls:
        :param object: Managed Object
        :param status: True - if object is down, False - otherwise
<<<<<<< HEAD
        :param ts: Effective event timestamp. None for current time
        :return:
        """
        ts = ts or datetime.datetime.now()
        col = Outage._get_collection()
        lo = col.find_one({
            "object": object.id,
            "start": {
                "$lte": ts
            }
        }, {
            "_id": 1,
            "stop": 1
        }, sort=[("object", 1), ("start", -1)])
        if not status and lo and not lo.get("stop"):
            # Close interval
            col.update({
                "_id": lo["_id"]
            }, {
                "$set": {
                    "stop": ts
                }
            })
        elif status and (not lo or lo.get("stop")):
            # New outage
            col.insert({
                "object": object.id,
                "start": ts,
                "stop": None
            })
=======
        :return:
        """
        ts = datetime.datetime.now()
        o = cls.objects.filter(object=object.id,
            start__lte=datetime.datetime.now()).order_by("-start").first()
        if o and o.is_active and not status:
            # Close active outage
            o.stop = ts
            o.save()
        elif status and ((o and not o.is_active) or not o):
            # Create new outage
            Outage(object=object.id, start=ts, stop=None).save()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
