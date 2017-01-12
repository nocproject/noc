# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Memcached backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
import pylibmc
import pylibmc.pools
## NOC modules
from base import BaseCache
from noc.core.config.base import config

logger = logging.getLogger(__name__)


class MemcachedCache(BaseCache):
    """
    Memcached backend
    """
    def __init__(self):
        super(BaseCache, self).__init__()
        self.tpl_client = pylibmc.Client(
            config.memcached_hosts,
            binary=True,
            behaviors={
                "tcp_nodelay": True,
                # Failover handling
                "ketama": True,
                "remove_failed": 1,
                "retry_timeout": 1,
                "dead_timeout": 60
            }
        )
        logger.debug(
            "Starting memcached pool: hosts=%s, pool size=%d",
            ", ".join(config.memcached_hosts),
            config.memcached_pool_size
        )
        self.pool = pylibmc.pools.ClientPool()
        self.pool.fill(self.tpl_client, config.memcached_pool_size)

    def get(self, key, default=None, version=None):
        """
        Returns value or raise KeyError
        :param key:
        :return:
        """
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            v = c.get(k)
        if v is None:
            return default
        else:
            return v

    def set(self, key, value, ttl=None, version=None):
        """
        Set key
        :param key:
        :param value:
        :param ttl:
        :param version:
        :return:
        """
        k = self.make_key(key, version)
        ttl = ttl or config.memcached_default_ttl
        with self.pool.reserve(block=True) as c:
            c.set(k, value, ttl)

    def delete(self, key, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            c.delete(k)

    def get_many(self, keys, version=None):
        k = [self.make_key(x, version) for x in keys]
        with self.pool.reserve(block=True) as c:
            r = c.get_multi(k)
        if r:
            m = dict(zip(k, keys))
            return dict((m[k], r[k]) for k in r)
        else:
            return None

    def set_many(self, data, ttl=None, version=None):
        ttl = ttl or config.memcached_default_ttl
        with self.pool.reserve(block=True) as c:
            c.set_multi(
                dict((self.make_key(k, version), data[k]) for k in data),
                ttl
            )

    def delete_many(self, keys, version=None):
        with self.pool.reserve(block=True) as c:
            c.delete_multi(
                [self.make_key(k, version) for k in keys]
            )

    def __getitem__(self, item):
        self.get(item)

    def __contains__(self, item):
        return self.has_key(item)

    def incr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            return c.incr(k, delta)

    def decr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            return c.decr(k, delta)
