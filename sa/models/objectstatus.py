# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ObjectStatus
# Updated by SAE according to ping check changes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, BooleanField, DateTimeField
from noc.fm.models.outage import Outage


class ObjectStatus(Document):
    meta = {
        "collection": "noc.cache.object_status",
        "strict": False,
        "indexes": ["object"]
    }
    # Object id
    object = IntField(required=True)
    # True - object is Up
    # False - object is Down
    status = BooleanField()
    # Last update
    last = DateTimeField()

    def __unicode__(self):
        return u"%s: %s" % (self.object, self.status)

    @classmethod
    def get_status(cls, object):
        d = ObjectStatus._get_collection().find_one({
            "object": object.id
        })
        if d:
            return d["status"]
        else:
            return True

    @classmethod
    def get_last_status(cls, object):
        """
        Returns last registred status and update time
        :param object: Managed Object id
        :return: last status, last update or None
        """
        d = ObjectStatus._get_collection().find_one({
            "object": object.id
        })
        if d:
            return d["status"], d.get("last")
        else:
            return None, None

    @classmethod
    def get_statuses(cls, objects):
        """
        Returns a map of object id -> status
        for a list od object ids
        """
        s = {}
        c = cls._get_collection()
        while objects:
            chunk, objects = objects[:500], objects[500:]
            for d in c.find({"object": {"$in": chunk}}):
                s[d["object"]] = d["status"]
        return s

    @classmethod
    def set_status(cls, object, status, ts=None):
        """
        Update object status
        :param object: Managed Object instance
        :param status: New status
        :param ts: Status change timestamp
        :return: True, if status has been changed, False - out-of-order update
        """
        ts = ts or datetime.datetime.now()
        coll = ObjectStatus._get_collection()
        # Update naively
        # Must work in most cases
        # find_and_modify returns old document or None for upsert
        r = coll.find_and_modify({
            "object": object.id
        }, update={
            "$set": {
                "status": status,
                "last": ts
            }
        }, upsert=True)
        if not r:
            # Setting status for first time
            # Work complete
            return True
        if r["last"] > ts:
            # Oops, out-of-order update
            # Restore correct state
            coll.update({
                "object": object.id
            }, {
                "status": r["status"],
                "last": r["last"]
            })
            return False
        if r["status"] != status:
            # Status changed
            Outage.register_outage(object, not status, ts=ts)
        return True
