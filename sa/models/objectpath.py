# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ObjectPath
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import operator
# Python modules
from threading import Lock

import cachetools
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import ListField, ObjectIdField, IntField

id_lock = Lock()


class ObjectPath(Document):
    meta = {
        "collection": "noc.cache.objectpaths",
        "strict": False,
        "auto_create_index": False,
    }
    # Object id
    object = IntField(primary_key=True)
    adm_path = ListField(IntField())
    segment_path = ListField(ObjectIdField())
    container_path = ListField(ObjectIdField())

    _object_cache = cachetools.TTLCache(10000, ttl=300)

    @classmethod
    def refresh(cls, obj):
        ObjectPath._get_collection().update(
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

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_object_cache"), lock=lambda _: id_lock)
    def _get_path(cls, object_id):
        return ObjectPath.objects.filter(object=object_id).first()

    @classmethod
    def get_path(cls, object):
        if hasattr(object, "id"):
            object = object.id
        return cls._get_path(object)
