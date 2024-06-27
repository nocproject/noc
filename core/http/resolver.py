# ----------------------------------------------------------------------
# Resolver module
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
import asyncio
import threading
import random
from typing import Optional

# Third-party modules
import cachetools

# NOC modules
from noc.config import config

ns_lock = threading.Lock()
ns_cache = cachetools.TTLCache(
    config.http_client.ns_cache_size, ttl=config.http_client.resolver_ttl
)


async def resolve_async(host: str) -> Optional[str]:
    """
    Resolve host and return address
    :param host:
    :return:
    """
    with ns_lock:
        addrs = ns_cache.get(host)
    if addrs:
        return random.choice(addrs)
    try:
        addr_info = await asyncio.get_running_loop().getaddrinfo(
            host, None, proto=socket.IPPROTO_TCP
        )
        addrs = [x[4][0] for x in addr_info if x[0] == socket.AF_INET]
        if not addrs:
            return None
        with ns_lock:
            ns_cache[host] = addrs
        return random.choice(addrs)
    except socket.gaierror:
        return None


def resolve_sync(host: str) -> Optional[str]:
    """
    Resolve host and return address
    :param host:
    :return:
    """
    with ns_lock:
        addrs = ns_cache.get(host)
    if addrs:
        return random.choice(addrs)
    try:
        addr_info = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
        addrs = [x[4][0] for x in addr_info if x[0] == socket.AF_INET]
        if not addrs:
            return None
        with ns_lock:
            ns_cache[host] = addrs
        return random.choice(addrs)
    except socket.gaierror:
        return None
