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
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BinaryField,
                                DateTimeField, IntField)
import bson

CURRENT_VERSION = 1


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
        decoder = getattr(cls, "decode_v%s" % d.get("version", CURRENT_VERSION))
        return decoder(d["data"])

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
        data = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)
        return zlib.compress(data)

    @classmethod
    def decode_v1(cls, data):
        """
        v2 decoding: cPickle + zlib.compress
        :param data:
        :return:
        """
        data = zlib.decompress(data)
        return cPickle.loads(data)
