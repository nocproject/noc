# ----------------------------------------------------------------------
# Redis backend
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pickle import loads, dumps, HIGHEST_PROTOCOL

# Third-party modules
import redis

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from .base import BaseCache

ignorable_redis_errors = (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError)


class RedisCache(BaseCache):
    def __init__(self):
        super().__init__()
        self.redis = redis.StrictRedis(
            host=config.redis.addresses[0].host,
            port=config.redis.addresses[0].port,
            db=config.redis.db,
        )

    @staticmethod
    def serialize(v):
        """Convert value to wire format"""
        return dumps(v, HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize(v):
        """Convert wire format to value"""
        if v is None:
            return v
        return loads(v)

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
            v = self.deserialize(self.redis.get(k))
        except ignorable_redis_errors:  # pylint: disable-msg=E0712
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
            self.redis.set(k, self.serialize(value), ex=ttl)
        except ignorable_redis_errors:  # pylint: disable-msg=E0712
            metrics["error", ("type", "redis_set_failed")] += 1

    def delete(self, key, version=None):
        # pylint: disable-msg=E0712
        k = self.make_key(key, version)
        try:
            self.redis.delete(k)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_delete_failed")] += 1

    def get_many(self, keys, version=None):
        # pylint: disable-msg=E0712
        k = [self.make_key(x, version) for x in keys]
        try:
            r = self.redis.mget(k)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_get_many_failed")] += 1
            return None
        return {k: self.deserialize(v) for k, v in zip(keys, r)}

    def set_many(self, data, ttl=None, version=None):
        # pylint: disable-msg=E0712
        ttl = ttl or config.redis.default_ttl
        pipe = self.redis.pipeline()
        for k in data:
            pipe.set(self.make_key(k, version), self.serialize(data[k]), ex=ttl)
        try:
            pipe.execute()
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_set_many_failed")] += 1

    def delete_many(self, keys, version=None):
        # pylint: disable-msg=E0712
        keys = [self.make_key(k, version) for k in keys]
        if not keys:
            return
        try:
            self.redis.delete(*keys)
        except ignorable_redis_errors:
            metrics["error", ("type", "redis_delete_many_failed")] += 1
