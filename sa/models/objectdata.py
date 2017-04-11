# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObjectData
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from threading import Lock
import operator
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, ListField
import cachetools
import six

id_lock = Lock()
neighbor_lock = Lock()


class ObjectData(Document):
    meta = {
        "collection": "noc.objectdata",
        "indexes": ["uplinks"]
    }
    object = IntField(primary_key=True)
    uplinks = ListField(IntField())

    _id_cache = cachetools.TTLCache(10000, ttl=120)
    _neighbor_cache = cachetools.TTLCache(1000, ttl=300)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return ObjectData.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_neighbor_cache"), lock=lambda _: neighbor_lock)
    def _get_neighbors(cls, object_id):
        n = set()
        for d in ObjectData._get_collection().find({
            "uplinks": object_id
        }, {
            "_id": 1
        }):
            n.add(d["_id"])
        return list(n)

    @classmethod
    def get_neighbors(cls, object):
        if hasattr(object, "id"):
            object = object.id
        return cls._get_neighbors(object)

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
        for d in ObjectData._get_collection().find({
            "_id": {
                "$in": o
            }
        }, {"_id": 1, "uplinks": 1}):
            uplinks[d["_id"]] = d["uplinks"]
        return uplinks

    @classmethod
    def update_uplinks(cls, umap):
        if not umap:
            return
        bulk = ObjectData._get_collection().initialize_unordered_bulk_op()
        for o, uplinks in six.iteritems(umap):
            bulk.find({
                "_id": o
            }).upsert().update({
                "$set": {
                    "uplinks": uplinks
                }
            })
        bulk.execute()
