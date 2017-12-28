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
from noc.config import config
from noc.core.perf import metrics

# NOC modules
from .base import BaseCache

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
            [str(a) for a in config.memcached.addresses],
            binary=True,
            behaviors={
                "tcp_nodelay": True
            }
        )
        logger.debug(
            "Starting memcached pool: hosts=%s, pool size=%d",
            ", ".join([str(a) for a in config.memcached.addresses]),
            config.memcached.pool_size
        )
        self.pool = pylibmc.pools.ClientPool()
        self.pool.fill(self.tpl_client, config.memcached.pool_size)

    def get(self, key, default=None, version=None):
        """
        Returns value or raise KeyError
        :param key:
        :param default:
        :param version:
        :return: value
        """
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as cache:
            try:
                v = cache.get(k)
            except ignorable_memcache_errors:
                metrics["error", ("type", "get")] += 1
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
        with self.pool.reserve(block=True) as cache:
            try:
                cache.set(k, value, ttl)
            except ignorable_memcache_errors:
                metrics["error", ("type", "set")] += 1

    def delete(self, key, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as cache:
            try:
                cache.delete(k)
            except ignorable_memcache_errors:
                metrics["error", ("type", "delete")] += 1

    def get_many(self, keys, version=None):
        k = [self.make_key(x, version) for x in keys]
        with self.pool.reserve(block=True) as cache:
            try:
                r = cache.get_multi(k)
            except ignorable_memcache_errors:
                metrics["error", ("type", "get_many")] += 1
                r = None
        if r:
            m = dict(zip(k, keys))
            return dict((m[k], r[k]) for k in r)
        else:
            return None

    def set_many(self, data, ttl=None, version=None):
        ttl = ttl or config.memcached.default_ttl
        with self.pool.reserve(block=True) as cache:
            try:
                cache.set_multi(
                    dict((self.make_key(k, version), data[k])
                         for k in data),
                    ttl
                )
            except ignorable_memcache_errors:
                metrics["error", ("type", "set_many")] += 1

    def delete_many(self, keys, version=None):
        with self.pool.reserve(block=True) as cache:
            try:
                cache.delete_multi(
                    [self.make_key(k, version) for k in keys]
                )
            except ignorable_memcache_errors:
                metrics["error", ("type", "delete_many")] += 1

    def incr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as cache:
            try:
                return cache.incr(k, delta)
            except ignorable_memcache_errors:
                metrics["error", ("type", "incr")] += 1
                return None

    def decr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        with self.pool.reserve(block=True) as cache:
            try:
                return cache.decr(k, delta)
            except ignorable_memcache_errors:
                metrics["error", ("type", "decr")] += 1
                return None
