# ----------------------------------------------------------------------
# Load config from consul
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""Consul-based configuration backend.

This module implements configuration loading from Consul KV storage.

The backend URL format is::

    consul://<host>:<port>/<path>?token=<token>

Consul keys are converted into a hierarchical configuration tree and can be
accessed using dot-separated configuration keys.
"""

# Python modules
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from functools import cached_property
from urllib.parse import urlparse, unquote

# Third-party modules
from consul.exceptions import Timeout

# NOC modules
from noc.core.consul import ConsulClient
from noc.core.comp import smart_text
from noc.core.ioloop.util import run_sync
from .base import DataConfigBackend

DEFAULT_CONSUL_PORT = 8500


@dataclass
class ConsulParams:
    """Consul backend parameters.

    Args:
        host: Consul server hostname or IP address.
        port: Consul server port.
        path: KV storage path used as configuration root.
        token: Optional Consul authentication token.
    """

    host: str
    port: int
    path: str
    token: str | None = None

    @classmethod
    def from_url(cls, url: str) -> ConsulParams:
        """Parse Consul backend parameters from URL.

        Args:
            url: Consul backend URL.

        Returns:
            Parsed Consul backend parameters.
        """
        parsed = urlparse(url)
        # Get token
        token = None
        for q in parsed.query.split("&"):
            if q.startswith("token="):
                token = unquote(q[6:])
                break
        return ConsulParams(
            host=parsed.hostname or "",
            port=parsed.port or DEFAULT_CONSUL_PORT,
            path=parsed.path[1:],
            token=token,
        )


class ConsulBackend(DataConfigBackend):
    """Configuration backend backed by Consul KV storage.

    URL format::

        consul://<host>:<port>/<path>?token=<token>

    The specified KV path is loaded recursively. Consul key paths are converted
    into a nested dictionary structure.
    """

    @cached_property
    def params(self) -> ConsulParams:
        """Return parsed backend parameters.

        Returns:
            Consul backend parameters.
        """
        return ConsulParams.from_url(self.url)

    async def get_kv(self) -> list[dict[str, object]] | None:
        """Fetch configuration keys from Consul KV storage.

        The request is retried indefinitely when Consul returns a timeout.
        A recursive lookup is performed starting from the configured KV path.

        Returns:
            List of Consul KV entries or None if no entries are available.

        """
        params = self.params
        client = ConsulClient(host=params.host, port=params.port, token=params.token)
        while True:
            try:
                return await client.kv.get(params.path, recurse=True, token=params.token)
            except Timeout:
                await asyncio.sleep(2)

    def get_data(self) -> dict[str, object] | None:
        """Load configuration data from Consul.

        The method performs a recursive KV lookup and converts returned keys
        into a nested configuration dictionary.

        Returns:
            Configuration mapping or None when no data is available.
        """

        async def get() -> dict[str, object] | None:
            params = self.params
            # Convert to dict
            data = {}
            if params.path.endswith("/"):
                pl = len(params.path)
            else:
                pl = len(params.path) + 1
            kv_data = await self.get_kv()
            if not kv_data:
                return None
            for i in kv_data:
                k = i["Key"][pl:]
                v = i["Value"]
                if "slots" in k or k.endswith("/"):
                    # Section
                    continue
                if v in (b'""', b"''"):
                    # fix if value is "" - return '""'
                    v = ""
                *path, k1 = k.split("/")
                c = data
                for p in path:
                    if p not in c:
                        c[p] = {}
                        c = c[p]
                    else:
                        c = c[p]
                c[k1] = smart_text(v)
            return data

        return run_sync(get)
