# ----------------------------------------------------------------------
# BaseCache
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Any, Iterable

# NOC modules
from noc.config import config
from noc.core.handler import get_handler

logger = logging.getLogger(__name__)


class BaseCache:
    """
    Basic cache class.
    Follows common dict style like cache[key] = value
    """

    @staticmethod
    def make_key(key: str, version: int | None = None) -> str:
        return f"{key}|{version or 0}"

    def get(self, key: str, default: Any | None = None, version: int | None = None) -> Any | None:
        """
        Returns value or raise KeyError
        :return:
        """
        return default

    def set(self, key: str, value: Any, ttl: int | None = None, version: int | None = None) -> None:
        """
        Set key
        :return:
        """

    def delete(self, key: str, version: Any | None = None) -> None:
        pass

    def has_key(self, key: str, version: int | None = None) -> bool:
        return self.get(key, version=version) is not None

    def get_many(self, keys: Iterable, version: int | None = None) -> dict[str, Any]:
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
        self, data: dict[str, Any], ttl: int | None = None, version: int | None = None
    ) -> None:
        for k in data:
            self.set(k, data[k], ttl=ttl, version=version)

    def delete_many(self, keys: Iterable, version: int | None = None) -> None:
        for k in keys:
            self.delete(k, version=version)

    def __getitem__(self, item: str) -> Any | None:
        return self.get(item)

    def __contains__(self, item: str) -> bool:
        return self.get(item) is not None

    @classmethod
    def get_cache(cls) -> "BaseCache":
        cache_cls = config.cache.cache_class
        logger.info("Using cache backend: %s", cache_cls)
        c = get_handler(cache_cls)
        if c:
            return c()
        logger.error("Cannot load cache backend: Fallback to dummy")
        return BaseCache()


# cache singleton
cache = BaseCache.get_cache()
