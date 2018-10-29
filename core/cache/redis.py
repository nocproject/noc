# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Redis backend
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import redis
# NOC modules
from noc.config import config
from noc.core.perf import metrics
from .base import BaseCache

ignorable_redis_errors = (
    redis.exceptions.ConnectionError,
    redis.exceptions.TimeoutError
)


class RedisCache(BaseCache):
    def __init__(self):
        super(RedisCache, self).__init__()
        self.redis = redis.StrictRedis(
            host=config.redis.addresses[0].host,
            port=config.redis.addresses[0].port,
            db=config.redis.db
        )

    def get(self, key, default=None, version=None):
        """
        Returns value or raise KeyError
        :param key:
        :param default:
        :param version:
        :return: value
        """
        k = self.make_key(key, version)
        try:
            v = self.redis.get(k)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_get_failed")] += 1
            v = None
        if v is None:
            return default
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
        ttl = ttl or config.redis.default_ttl
        try:
            self.redis.set(k, value, ex=ttl)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_set_failed")] += 1

    def delete(self, key, version=None):
        k = self.make_key(key, version)
        try:
            self.redis.delete(k)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_delete_failed")] += 1

    def get_many(self, keys, version=None):
        k = [self.make_key(x, version) for x in keys]
        try:
            r = self.redis.mget(k)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_get_many_failed")] += 1
            return None
        return dict(zip(keys, r))

    def set_many(self, data, ttl=None, version=None):
        ttl = ttl or config.redis.default_ttl
        pipe = self.redis.pipeline()
        for k in data:
            pipe.set(self.make_key(k, version), data[k], ex=ttl)
        try:
            pipe.execute()
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_set_many_failed")] += 1

    def delete_many(self, keys, version=None):
        try:
            self.redis.delete(*[self.make_key(k, version) for k in keys])
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_delete_many_failed")] += 1

    def incr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        try:
            return self.redis.incr(k, delta)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_incr_failed")] += 1

    def decr(self, key, delta=1, version=None):
        k = self.make_key(key, version)
        try:
            return self.redis.decr(k, delta)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_decr_failed")] += 1
