# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BaseCache
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.core.config.base import config
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)


class BaseCache(object):
    """
    Basic cache class.
    Follows common dict style like cache[key] = value
    """
    @staticmethod
    def make_key(key, version=None):
        return "%s|%s" % (key, version or 0)

    def get(self, key, default=None, version=None):
        """
        Returns value or raise KeyError
        :param key:
        :return:
        """
        return default

    def set(self, key, value, ttl=None, version=None):
        """
        Set key
        :param key:
        :param value:
        :param ttl:
        :return:
        """
        pass

    def delete(self, key, version=None):
        pass

    def has_key(self, key, version=None):
        return self.get(key, version=version) is not None

    def get_many(self, keys, version=None):
        """
        Fetch a bunch of keys from the cache.
        """
        d = {}
        for k in keys:
            val = self.get(k, version=version)
            if val is not None:
                d[k] = val
        return d

    def set_many(self, data, ttl=None, version=None):
        for k in data:
            self.set(k, data[k], ttl=ttl, version=version)

    def delete_many(self, keys, version=None):
        for k in keys:
            self.delete(k, version=None)

    def __getitem__(self, item):
        self.get(item)

    def __contains__(self, item):
        return self.get(item) is not None

    def incr(self, key, delta=1, version=None):
        value = self.get(key, version=version)
        if value is None:
            raise ValueError("Key '%s' not found" % key)
        new_value = value + delta
        self.set(key, new_value, version=version)
        return new_value

    def decr(self, key, delta=1, version=None):
        return self.incr(key, -delta, version=version)

    @classmethod
    def get_cache(cls):
        h = config.cache_class
        logger.info("Using cache backend: %s", h)
        c = get_handler(h)
        if c:
            return c()
        else:
            logger.error("Cannot load cache backend: Fallback to dummy")
            return BaseCache()

## cache singleton
cache = BaseCache.get_cache()
