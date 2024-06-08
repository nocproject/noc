# ----------------------------------------------------------------------
# BaseCache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Any, Iterable, Dict
import warnings

# NOC modules
from noc.config import config
from noc.core.handler import get_handler
from noc.core.deprecations import RemovedInNOC2402Warning

logger = logging.getLogger(__name__)


class BaseCache(object):
    """
    Basic cache class.
    Follows common dict style like cache[key] = value
    """

    @staticmethod
    def make_key(key: str, version: Optional[int] = None) -> str:
        return "%s|%s" % (key, version or 0)

    def get(
        self, key: str, default: Optional[Any] = None, version: Optional[int] = None
    ) -> Optional[Any]:
        """
        Returns value or raise KeyError
        :param key:
        :param version:
        :param default:
        :return:
        """
        return default

    def set(
        self, key: str, value: Any, ttl: Optional[int] = None, version: Optional[int] = None
    ) -> None:
        """
        Set key
        :param key:
        :param value:
        :param ttl:
        :return:
        """

    def delete(self, key: str, version: Optional[Any] = None) -> None:
        pass

    def has_key(self, key: str, version: Optional[int] = None) -> bool:
        return self.get(key, version=version) is not None

    def get_many(self, keys: Iterable, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch a bunch of keys from the cache.
        """
        d = {}
        for k in keys:
            val = self.get(k, version=version)
            if val is not None:
                d[k] = val
        return d

    def set_many(
        self, data: Dict[str, Any], ttl: Optional[int] = None, version: Optional[int] = None
    ) -> None:
        for k in data:
            self.set(k, data[k], ttl=ttl, version=version)

    def delete_many(self, keys: Iterable, version: Optional[int] = None) -> None:
        for k in keys:
            self.delete(k, version=version)

    def __getitem__(self, item: str) -> Optional[Any]:
        return self.get(item)

    def __contains__(self, item: str) -> bool:
        return self.get(item) is not None

    @classmethod
    def get_cache(cls) -> "BaseCache":
        cache_cls = config.cache.cache_class
        if cache_cls == "noc.core.cache.memcached.MemcachedCache":
            warnings.warn(
                "Memcached cache is deprecated and not safe. Switching to mongo cache. Will be an error in NOC 24.2",
                RemovedInNOC2402Warning,
            )
            cache_cls = "noc.core.cache.mongo.MongoCache"
        logger.info("Using cache backend: %s", cache_cls)
        c = get_handler(cache_cls)
        if c:
            return c()
        logger.error("Cannot load cache backend: Fallback to dummy")
        return BaseCache()


# cache singleton
cache = BaseCache.get_cache()
