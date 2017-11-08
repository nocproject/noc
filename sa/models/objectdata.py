# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ManagedObjectData
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import operator
# Python modules
from threading import Lock

import cachetools
import six
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, ListField, ObjectIdField

id_lock = Lock()
neighbor_lock = Lock()


class ObjectData(Document):
    meta = {
        "collection": "noc.objectdata",
        "indexes": ["uplinks"]
    }
    object = IntField(primary_key=True)
    # Uplinks
    uplinks = ListField(IntField())
    # Paths
    adm_path = ListField(IntField())
    segment_path = ListField(ObjectIdField())
    container_path = ListField(ObjectIdField())

    _id_cache = cachetools.TTLCache(10000, ttl=120)
    _neighbor_cache = cachetools.TTLCache(1000, ttl=300)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def _get_by_id(cls, object_id):
        return ObjectData.objects.filter(object=object_id).first()

    @classmethod
    def get_by_id(cls, object):
        if hasattr(object, "id"):
            object = object.id
        return cls._get_by_id(object)

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
            uplinks[d["_id"]] = d.get("uplinks", [])
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

    @classmethod
    def refresh_path(cls, obj):
        ObjectData._get_collection().update(
            {
                "_id": obj.id
            },
            {
                "$set": {
                    "adm_path": obj.administrative_domain.get_path(),
                    "segment_path": obj.segment.get_path(),
                    "container_path": obj.container.get_path() if obj.container else []
                }
            },
            upsert=True
        )
