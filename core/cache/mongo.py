# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Mongo backend
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
# Third-party modules
import bson
from six.moves.cPickle import loads, dumps, HIGHEST_PROTOCOL
# NOC modules
from .base import BaseCache
from noc.lib.nosql import get_db
from noc.core.config.base import config


class MongoCache(BaseCache):
    collection_name = "noc.caches.mongo"
    KEY_FIELD = "_id"
    VALUE_FIELD = "v"
    EXPIRES_FIELD = "x"

    @classmethod
    def get_collection(cls):
        if not hasattr(cls, "_collection"):
            cls._collection = get_db()[cls.collection_name]
            cls.ensure_indexes()
        return cls._collection

    @classmethod
    def ensure_indexes(cls):
        cls._collection.ensure_index(
            cls.EXPIRES_FIELD, expireAfterSeconds=0
        )

    def get(self, key, default=None, version=None):
        k = self.make_key(key, version)
        now = datetime.datetime.now()
        d = self.get_collection().find_one({
            self.KEY_FIELD: k
        })
        if d and d[self.EXPIRES_FIELD] > now:
            # Found, not expired
            return loads(d[self.VALUE_FIELD])
        else:
            return default

    def set(self, key, value, ttl=None, version=None):
        """
        Set key
        :param key:
        :param value:
        :param ttl:
        :return:
        """
        k = self.make_key(key, version)
        ttl = ttl or config.memcached_default_ttl
        expires = datetime.datetime.now() + datetime.timedelta(seconds=ttl)
        self.get_collection().update({
            self.KEY_FIELD: k
        }, {
            "$set": {
                self.VALUE_FIELD: bson.Binary(
                    dumps(value, HIGHEST_PROTOCOL)),
                self.EXPIRES_FIELD: expires
            }
        }, upsert=True)

    def delete(self, key, version=None):
        k = self.make_key(key, version)
        self.get_collection().remove({
            self.KEY_FIELD: k
        })
