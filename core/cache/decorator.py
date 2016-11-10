# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Decorators
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import cache as x_cache
from noc.core.perf import metrics


def cachedmethod(cache=None, key="cache-%s", lock=None, ttl=None):
    """
    Decorator to wrap class instance or method
    with memoizing callable
    :param cache: In-memory function which follows dict protocol.
        None, when no in-memory caching required
    :param key: Key mask to convert args to string
    :param lock: Callable to get threading lock
    :return:
    """
    def decorator(method):
        if lock:
            def wrapper(self, *args, **kwargs):
                perf_key = key.replace("%s", "X").replace("-", "_")
                perf_key_requests = metrics["%s_requests" % perf_key]
                perf_key_l1_hits = metrics["%s_l1_hits" % perf_key]
                perf_key_l2_hits = metrics["%s_l2_hits" % perf_key]
                perf_key_misses = metrics["%s_misses" % perf_key]
                perf_key_lock_acquires = metrics["%s_locks_acquires" % perf_key]
                perf_key_requests += 1
                k = key % args
                with lock(self):
                    perf_key_lock_acquires += 1
                    if cache:
                        # Try in-memory cache
                        c = cache(self)
                        if c is not None:
                            # In-memory cache provided
                            try:
                                v = c[k]
                                perf_key_l1_hits += 1
                                return v
                            except KeyError:
                                pass
                # Try external cache
                v = x_cache.get(k)
                if v:
                    perf_key_l2_hits += 1
                    if cache:
                        with lock(self):
                            perf_key_lock_acquires += 1
                            # Backfill in-memory cache
                            try:
                                c[k] = v
                            except ValueError:
                                pass  # Value too large
                    return v
                # Fallback to function
                perf_key_misses += 1
                v = method(self, *args, **kwargs)
                with lock(self):
                    perf_key_lock_acquires += 1
                    if cache:
                        # Backfill in-memory cache
                        try:
                            c[k] = v
                        except ValueError:
                            pass
                    # Backfill external cache
                    x_cache.set(k, v, ttl=ttl)
                # Done
                return v
        else:
            def wrapper(self, *args, **kwargs):
                perf_key = key.replace("%s", "X").replace("-", "_")
                perf_key_requests = metrics["%s_requests" % perf_key]
                perf_key_l1_hits = metrics["%s_l1_hits" % perf_key]
                perf_key_l2_hits = metrics["%s_l2_hits" % perf_key]
                perf_key_misses = metrics["%s_misses" % perf_key]
                perf_key_lock_acquires = metrics["%s_locks_acquires" % perf_key]
                perf_key_requests += 1
                k = key % args
                if cache:
                    # Try in-memory cache
                    c = cache(self)
                    if c is not None:
                        # In-memory cache provided
                        try:
                            v = c[k]
                            perf_key_l1_hits += 1
                            return v
                        except KeyError:
                            pass
                # Try external cache
                v = x_cache.get(k)
                if v:
                    perf_key_l2_hits += 1
                    if cache:
                        # Backfill in-memory cache
                        try:
                            c[k] = v
                        except ValueError:
                            pass  # Value too large
                    return v
                # Fallback to function
                perf_key_misses += 1
                v = method(self, *args, **kwargs)
                if cache:
                    # Backfill in-memory cache
                    try:
                        c[k] = v
                    except ValueError:
                        pass
                # Backfill external cache
                x_cache.set(k, v, ttl=ttl)
                # Done
                return v
        return wrapper

    return decorator
