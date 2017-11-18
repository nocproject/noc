# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataSourceCache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import logging
import datetime
import bz2
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BinaryField,
                                DateTimeField, IntField)
import bson

logger = logging.getLogger(__name__)
CURRENT_VERSION = 2
# 16777216 Max MongoDB Document size - 16Mb
MAX_DATA_SIZE = 16 * 1024 * 1024 - 1024 * 1024


class DataSourceCache(Document):
    meta = {
        "collection": "datasource_cache",
        "strict": False,
        "auto_create_index": False,
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
        # Compressed size: 17425159
        data = cls.encode(data)
        size = sys.getsizeof(data)
        if size > MAX_DATA_SIZE:
            logger.warning("[%s] Compressed size data: %s over max size %s" % (name, size, MAX_DATA_SIZE))
        else:
            cls._get_collection().update({
                "_id": name
            }, {
                "$set": {
                    "data": bson.Binary(data),
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
