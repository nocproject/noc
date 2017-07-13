# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Memcached backend
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
# Third-party modules
import pylibmc
import pylibmc.pools
# NOC modules
from .base import BaseCache
from noc.config import config

logger = logging.getLogger(__name__)
ignorable_memcache_errors = (
    pylibmc.ConnectionError,
    pylibmc.ServerDown
)


class MemcachedCache(BaseCache):
    """
    Memcached backend
    """
    def __init__(self):
        super(BaseCache, self).__init__()
        self.tpl_client = pylibmc.Client(
            [str(a) for a in config.nsqlookupd.addresses],
            binary=True,
            behaviors={
                "tcp_nodelay": True
            }
        )
        logger.debug(
            "Starting memcached pool: hosts=%s, pool size=%d",
            ", ".join([str(a) for a in config.nsqlookupd.addresses]),
            config.memcached.pool_size
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
            try:
                v = c.get(k)
            except ignorable_memcache_errors:
                v = None
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
        ttl = ttl or config.memcached.default_ttl
        with self.pool.reserve(block=True) as c:
            try:
                c.set(k, value, ttl)
            except ignorable_memcache_errors:
                pass

    def delete(self, key, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            try:
                c.delete(k)
            except ignorable_memcache_errors:
                pass

    def get_many(self, keys, version=None):
        k = [self.make_key(x, version) for x in keys]
        with self.pool.reserve(block=True) as c:
            try:
                r = c.get_multi(k)
            except ignorable_memcache_errors:
                r = None
        if r:
            m = dict(zip(k, keys))
            return dict((m[k], r[k]) for k in r)
        else:
            return None

    def set_many(self, data, ttl=None, version=None):
        ttl = ttl or config.memcached.default_ttl
        with self.pool.reserve(block=True) as c:
            try:
                c.set_multi(
                    dict((self.make_key(k, version), data[k])
                         for k in data),
                    ttl
                )
            except ignorable_memcache_errors:
                pass

    def delete_many(self, keys, version=None):
        with self.pool.reserve(block=True) as c:
            try:
                c.delete_multi(
                    [self.make_key(k, version) for k in keys]
                )
            except ignorable_memcache_errors:
                pass

    def incr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            try:
                return c.incr(k, delta)
            except ignorable_memcache_errors:
                return None

    def decr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as c:
            try:
                return c.decr(k, delta)
            except ignorable_memcache_errors:
                return None
