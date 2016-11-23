# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object uplink map
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, ListField
import cachetools

id_lock = Lock()


class ObjectUplink(Document):
    meta = {
        "collection": "noc.objectuplinks",
        "indexes": ["uplinks"]
    }
    object = IntField(primary_key=True)
    uplinks = ListField(IntField())

    _object_cache = cachetools.TTLCache(1000, ttl=60)

    @classmethod
    def update_uplinks(cls, umap):
        if not umap:
            return
        bulk = ObjectUplink._get_collection().initialize_unordered_bulk_op()
        for o, uplinks in umap.iteritems():
            bulk.find({"_id": o}).upsert().update({
                "$set": {
                    "uplinks": uplinks
                }
            })
        bulk.execute()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_object_cache"), lock=lambda _: id_lock)
    def _uplinks_for_object(cls, object_id):
        d = ObjectUplink._get_collection().find_one({"_id": object_id}, {"_id": 0, "uplinks": 1})
        if d:
            return d["uplinks"]
        return []

    @classmethod
    def uplinks_for_object(cls, object):
        if hasattr(object, "id"):
            object = object.id
        return cls._uplinks_for_object(object)

    @classmethod
    def uplinks_for_objects(cls, objects):
        """
        Returns uplinks for list of objects
        :param objects: List of object
        :return: dict of object id -> uplinks
        """
        o = []
        for obj in objects:
            if hasattr(obj, "id"):
                obj = obj.id
            o += [obj]
        uplinks = dict((obj, []) for obj in o)
        for d in ObjectUplink._get_collection().find({"_id": {"$in": o}}):
            uplinks[d["_id"]] = d["uplinks"]
        return uplinks
