# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataSourceCache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import cPickle
import zlib
import bz2
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BinaryField,
                                DateTimeField, IntField)
import bson

CURRENT_VERSION = 2


class DataSourceCache(Document):
    meta = {
        "collection": "datasource_cache",
        "strict": False,
        "indexes": [{
            "fields": ["expires"],
            "expireAfterSeconds": 0
        }]
    }

    name = StringField(primary_key=True)
    data = BinaryField()
    expires = DateTimeField()
    version = IntField()

    @classmethod
    def get_data(cls, name):
        """
        Load cached data
        :param name:
        :return:
        """
        d = cls._get_collection().find_one({"_id": name})
        if not d:
            return None
        if d["version"] < CURRENT_VERSION:
            # Version bump, rebuild cache
            return None
        return cls.decode(d["data"])

    @classmethod
    def set_data(cls, name, data, ttl):
        cls._get_collection().update({
            "_id": name
        }, {
            "$set": {
                "data": bson.Binary(cls.encode(data)),
                "version": CURRENT_VERSION,
                "expires": datetime.datetime.now() + datetime.timedelta(seconds=ttl)
            },
            "$setOnInsert": {
                "name": name
            }
        }, upsert=True)

    @classmethod
    def encode(cls, data):
        """
        v1 encoding: cPickle + zlib.compress
        :param data:
        :return:
        """
        return bz2.compress(data, 9)

    @classmethod
    def decode(cls, data):
        """
        v2 decoding: bz2
        :param data:
        :return:
        """
        return bz2.decompress(data)
