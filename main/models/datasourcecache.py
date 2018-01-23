# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DataSourceCache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import bz2
# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (StringField, BinaryField,
                                DateTimeField, IntField)
import bson

logger = logging.getLogger(__name__)
CURRENT_VERSION = 3
# 16777216 Max MongoDB Document size - 16Mb
# bzip decoder usually reduces size
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
    chunks = IntField(min_value=0, max_value=5)
    version = IntField()
    # Next chunk name
    next_name = StringField()

    @classmethod
    def get_data(cls, name):
        """
        Load cached data
        :param name:
        :return:
        """
        data = []
        coll = DataSourceCache._get_collection()
        while name:
            d = coll.find_one({"_id": name})
            if not d:
                # Not found or broken chain
                return None
            if d["version"] != CURRENT_VERSION:
                # Version bump, rebuild cache
                return None
            data += [d["data"]]
            # Proceed to next chunk when necessary
            name = d.get("next_name", None)
        # Finally, decode result
        # avoid string catenation whenever possible
        return cls.decode("".join(data) if len(data) > 1 else data[0])

    @classmethod
    def set_data(cls, name, data, ttl):
        """
        Write data to cache
        :param name:
        :param data:
        :param ttl:
        :return:
        """
        data = cls.encode(data)
        coll = DataSourceCache._get_collection()
        n_chunk = 0
        fmt_chunk_name = "%s.%%d" % name
        expires = datetime.datetime.now() + datetime.timedelta(seconds=ttl),
        while data:
            # Split chunk and rest of data
            chunk, data = data[:MAX_DATA_SIZE], data[MAX_DATA_SIZE:]
            # Generate next chunk name when data left
            if data:
                n_chunk += 1
                next_name = fmt_chunk_name % n_chunk
            else:
                next_name = None
            logger.info("Writing chunk %s", name)
            # Update chunk
            coll.update_one({
                "_id": name
            }, {
                "$set": {
                    "data": bson.Binary(chunk),
                    "version": CURRENT_VERSION,
                    "expires": expires,
                    "next_name": next_name
                },
                "$setOnInsert": {
                    "name": name
                }
            }, upsert=True)
            # Name for next chunk
            name = next_name

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
