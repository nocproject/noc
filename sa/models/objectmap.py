# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Object Mapping
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.nosql import Document, IntField, ListField, StringField


class ObjectMap(Document):
    meta = {
        "collection": "noc.cache.object_map",
        "allow_inheritance": False,
        "indexes": ["object", "collector"]
    }
    # Object id
    object = IntField(required=True, unique=True)
    #
    collector = IntField(required=True)
    #
    sources = ListField(StringField())

    def __unicode__(self):
        return u"%s: %s" % (self.object, self.sources)

    @classmethod
    def update_map(cls, object, collector, sources):
        if hasattr(object, "id"):
            object = object.id
        if hasattr(collector, "id"):
            collector = collector.id
        if not isinstance(sources, (list, tuple)):
            sources = [sources]
        cls._get_collection().update({
            "object": object
        }, {
            "$set": {
                "collector": collector,
                "sources": sources
            }
        }, upsert=True)

    @classmethod
    def delete_map(cls, object):
        if hasattr(object, "id"):
            object = object.id
        cls._get_collection().remove({
            "object": object
        })

    @classmethod
    def get_map(cls, collector):
        c = cls._get_collection()
        return list(
            c.find({"collector": collector}, {"object": 1, "sources": 1, "_id": 0})
        )
