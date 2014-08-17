# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Caching engine
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import cPickle
import time
import datetime
## Django modules
from django.core.cache.backends.db import BaseDatabaseCache
## Third-party modules
import bson
## NOC modules
from noc.lib.nosql import get_db
from noc.lib.serialize import pickle
from noc.main.models.cache import Cache as CacheCollection


class Cache(object):
    """
    @todo: Deprecated. Replace with caching backend
    """
    # collection name is noc.cache.<cache_id>
    cache_id = ""
    ttl = 60

    def __init__(self):
        c = self.get_collection()
        c.ensure_index([("key", 1)])

    @classmethod
    def get_collection(cls):
        return get_db().noc.cache[cls.cache_id]

    @classmethod
    def get_key(cls, *args, **kwargs):
        """
        Called to calculate unique cache key
        :param cls:
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def find(cls, *args, **kwargs):
        """
        Called to find data when not found in cache
        :param cls:
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def set(self, value, *args, **kwargs):
        key = self.get_key(*args, **kwargs)
        c = self.get_collection()
        c.update({"key": key},
                {
                    "$set": {
                        "key": key,
                        "value": cPickle.dumps(value),
                        "expire": time.time() + self.ttl
                    }
                },
                upsert=True)

    def get(self, *args, **kwargs):
        key = self.get_key(*args, **kwargs)
        c = self.get_collection()
        t = time.time()
        # Try to find cached record
        r = c.find_one({"key": key})
        if r and r["expire"] > t:
            return cPickle.loads(str(r["value"]))
        # Refresh cache
        v = self.find(*args, **kwargs)
        # Update cache
        c.update({"key": key},
                {
                    "$set": {
                        "key": key,
                        "value": cPickle.dumps(v),
                        "expire": t + self.ttl
                    }
                },
                upsert=True)
        return v

    def refresh(self, *args, **kwargs):
        v = self.get(*args, **kwargs)
        self.set(v, *args, **kwargs)
        return v


class MongoDBCache(BaseDatabaseCache):
    """
    Based on https://github.com/django-nonrel/mongodb-cache
    """
    def validate_key(self, key):
        if "." in key or "$" in key:
            raise ValueError("Cache keys cannot contain '.' or '$'")
        super(MongoDBCache, self).validate_key(key)

    def get(self, key, default=None, version=None, raw=False, raw_key=False):
        if not raw_key:
            key = self.make_key(key, version=version)
        self.validate_key(key)
        collection = self._collection_for_read()
        document = collection.find_one({"_id": key})
        if document is None or document["e"] < datetime.datetime.now():
            return default
        if raw:
            return document
        pickled_obj = document.get("p")
        if pickled_obj is not None:
            return pickle.loads(pickled_obj)
        else:
            return document["v"]

    def has_key(self, key, version=None):
        return self.get(key, version=version, raw=True) is not None

    def set(self, key, value, timeout=None, version=None):
        self._base_set(key, value, timeout, version, force_set=True)

    def add(self, key, value, timeout=None, version=None):
        return self._base_set(key, value, timeout, version, force_set=False)

    def _base_set(self, key, value, timeout, version, force_set=False):
        collection = self._collection_for_write()
        if not force_set and self.has_key(key, version):
            # do not overwrite existing, non-expired entries.
            return False
        key = self.make_key(key, version=version)
        self.validate_key(key)
        now = datetime.datetime.now()
        secs = timeout or self.default_timeout
        expires = now + datetime.timedelta(seconds=secs)
        new_document = {"_id": key, "v": value, "e": expires}
        try:
            collection.save(new_document)
        except bson.errors.InvalidDocument:
            # value can't be serialized to BSON, fall back to pickle.
            # TODO: Suppress PyMongo warning here by writing a PyMongo patch
            # that allows BSON to be passed as document to .save
            pickle_blob = pickle.dumps(new_document.pop("v"), protocol=2)
            new_document["p"] = bson.binary.Binary(pickle_blob)
            collection.save(new_document)
        return True

    def incr(self, key, delta=1, version=None):
        key = self.make_key(key, version=version)
        collection = self._collection_for_write()
        new_document = collection.find_and_modify(
            {"_id": key},
            {"$inc": {"v": delta}},
            new=True, fields=["v"])
        if new_document is None:
            raise ValueError("Key %r not found" % key)
        return new_document["v"]

    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._collection_for_write().remove({"_id": key})

    def clear(self):
        self._collection_for_write().drop()

    def _collection_for_read(self):
        return CacheCollection._get_collection()

    def _collection_for_write(self):
        return CacheCollection._get_collection()
