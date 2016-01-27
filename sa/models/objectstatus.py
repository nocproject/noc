# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ObjectStatus
## Updated by SAE according to ping check changes
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, IntField, BooleanField


class ObjectStatus(Document):
    meta = {
        "collection": "noc.cache.object_status",
        "allow_inheritance": False,
        "indexes": ["object"]
    }
    # Object id
    object = IntField(required=True)
    # True - object is Up
    # False - object is Down
    status = BooleanField()

    def __unicode__(self):
        return u"%s: %s" % (self.object, self.status)

    @classmethod
    def get_status(cls, object):
        s = cls.objects.filter(object=object.id).first()
        if s:
            return s.status
        else:
            return True

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
        from noc.fm.models.outage import Outage

        s = cls.objects.filter(object=object.id).first()
        if s:
            if s.status != status:
                s.status = status
                s.save()
        else:
            cls(object=object.id, status=status).save()
        Outage.register_outage(object, not status, ts=ts)
