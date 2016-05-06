# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CredentialsCache
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import cPickle
import collections
## Third-party modules
from mongoengine.document import Document
from mongoengine.fields import IntField, BinaryField
import bson


class CredentialsCache(Document):
    meta = {
        "collection": "noc.cache.credentials",
        "allow_inheritance": False,
    }

    CURRENT_VERSION = 1

    object = IntField(primary_key=True)
    version = IntField(default=CURRENT_VERSION)
    value = BinaryField()

    @classmethod
    def get(cls, object):
        """
        Returns cached value or None
        """
        if hasattr(object, "id"):
            object = object.id
        doc = CredentialsCache._get_collection().find_one({
            "_id": object
        })
        if doc:
            if doc["version"] != cls.CURRENT_VERSION:
                return None
            else:
                return cPickle.loads(doc["value"])
        else:
            return None

    @classmethod
    def set(cls, object, value):
        if hasattr(object, "id"):
            object = object.id
        CredentialsCache._get_collection().update({
            "_id": object
        }, {
            "$set": {
                "version": CredentialsCache.CURRENT_VERSION,
                "value": bson.Binary(
                    cPickle.dumps(value, cPickle.HIGHEST_PROTOCOL)
                )
            }
        }, upsert=True)

    @classmethod
    def invalidate(cls, object):
        def q(o):
            if hasattr(o, "id"):
                return o.id
            else:
                return o

        if not object:
            return
        if isinstance(object, collections.Iterable):
            q = {
                "_id": {
                    "$in": [q(x) for x in object]
                }
            }
        else:
            q = {
                "_id": q(object)
            }
        CredentialsCache._get_collection().delete_one(q)
