# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BaseCache
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.nosql import get_db


class BaseCache(object):
    # Cache name
    name = None
    # Default expiration time
    ttl = datetime.timedelta(seconds=3600)
    #
    KEY_FIELD = "_id"
    VALUE_FIELD = "v"
    EXPIRES_FIELD = "x"

    def __init__(self):
        self.collection = self.get_collection()
        self.ensure_indexes()

    @classmethod
    def get_collection(cls):
        return get_db()["noc.cache.%s" % cls.name]

    @classmethod
    def ensure_indexes(cls):
        cls.get_collection().ensure_index(
            cls.EXPIRES_FIELD, expireAfterSeconds=0
        )

    def __missing__(self, item):
        """
        Override to populate cache
        """
        raise KeyError(item)

    def __getitem__(self, item):
        now = datetime.datetime.now()
        d = self.collection.find_one({
            self.KEY_FIELD: item
        })
        if d and d[self.EXPIRES_FIELD] > now:
            # Found, not expired
            return d[self.VALUE_FIELD]
        else:
            # Resolve and set
            value = self.__missing__(item)
            self[item] = value
            return value

    def __setitem__(self, key, value):
        expires = datetime.datetime.now() + self.ttl
        self.collection.update({
            self.KEY_FIELD: key
        }, {
            "$set": {
                self.VALUE_FIELD: value,
                self.EXPIRES_FIELD: expires
            }
        }, upsert=True)

    def __contains__(self, item):
        now = datetime.datetime.now()
        d = self.collection.find_one({
            self.KEY_FIELD: item
        })
        return d and d[self.EXPIRES_FIELD] > now

    def incr(self, key, value):
        raise NotImplementedError()
