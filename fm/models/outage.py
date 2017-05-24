# -*- coding: utf-8 -*-
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


class Outage(Document):
    meta = {
        "collection": "noc.fm.outages",
        "allow_inheritance": False,
        "indexes": ["object", ("object", "-start")]
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
