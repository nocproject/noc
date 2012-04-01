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
## NOC modules
from noc.lib.nosql import get_db


class Cache(object):
    """
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
