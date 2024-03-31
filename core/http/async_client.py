# ----------------------------------------------------------------------
# Synchronous HTTP Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from urllib.parse import urlparse
from typing import Optional, Dict, Tuple, Any, Callable

# Third-party modules
from gufo.http import BasicAuth, RequestMethod, DEFLATE, GZIP, BROTLI, Proxy, HttpError
from gufo.http.async_client import HttpClient as GufoHttpClient

# NOC modules
from noc.core.perf import metrics
from noc.core.comp import DEFAULT_ENCODING
from noc.config import config
from noc.core.validators import is_ipv4
from .proxy import SYSTEM_PROXIES

logger = logging.getLogger(__name__)

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
DEFAULT_PORTS = {"http": config.http_client.http_port, "https": config.http_client.https_port}


class HttpClient(GufoHttpClient):
    """
    Synchronous HTTP client.
    Attributes:
        headers: Headers to be added to every request.
            Used in subclasses.
        user_agent: Default user agent.
    Args:
        max_redirects: Maximal amount of redirects. Use `None`
            to disable redirect processing.
        compression: Acceptable compression methods,
            must be a combination of `DEFLATE`, `GZIP`, `BROTLI`.
            Set to `None` to disable compression support.
        validate_cert: Set to `False` to disable TLS certificate
            validation. Otherwise, raise `ConnectionError`
            on invalid certificates.
        connect_timeout: Timeout to establish connection, in seconds.
        timeout: Request timeout, in seconds.
        user: Authentication settings.
        password: Password
    """

    user_agent = config.http_client.user_agent

    def __init__(
        self: "HttpClient",
        /,
        max_redirects: Optional[int] = config.http_client.max_redirects,
        headers: Optional[Dict[str, bytes]] = None,
        compression: Optional[int] = DEFLATE | GZIP | BROTLI,
        validate_cert: bool = config.http_client.validate_certs,
        connect_timeout: float = config.http_client.connect_timeout,
        timeout: float = config.http_client.request_timeout,
        user_agent: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        allow_proxy=False,
        proxies=None,
        resolver=None,
    ) -> None:
        auth = None
        if user:
            auth = BasicAuth(user=user, password=password)
        if allow_proxy:
            proxy = (proxies or SYSTEM_PROXIES).get("https")
        else:
            proxy = None
        self.resolver: Optional[Callable] = resolver
        super().__init__(
            max_redirects=max_redirects,
            headers=headers,
            compression=compression,
            validate_cert=validate_cert,
            connect_timeout=connect_timeout,
            timeout=timeout,
            user_agent=user_agent or self.user_agent,
            auth=auth,
            proxy=[Proxy(proxy)] if proxy else None,
        )

    async def resolve(self, url: str) -> str:
        if not self.resolver:
            return url

        u = urlparse(str(url))
        if ":" in u.netloc:
            host, port = u.netloc.rsplit(":")
        else:
            host = u.netloc
        if is_ipv4(host):
            return url
        addr = await self.resolver(host)
        if not addr:
            raise TimeoutError("Cannot resolve host: %s" % host)
        if isinstance(addr, tuple):
            host = "%s:%s" % addr
        else:
            # Port ?
            host = addr
        return u._replace(netloc=host).geturl()

    async def request(
        self: "HttpClient",
        method: str,
        url: str,
        /,
        body: Optional[bytes] = None,
        headers: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[int, Dict[str, Any], bytes]:
        m = RequestMethod.get(method)
        if not m:
            raise NotImplementedError("Not implementer method: %s", method)
        metrics["httpclient_requests", ("method", method.lower())] += 1
        try:
            url = await self.resolve(url)
        except (TimeoutError, HttpError) as e:
            return ERR_TIMEOUT, {}, b"Cannot resolve host: %s" % str(e).encode(DEFAULT_ENCODING)
        try:
            r = await super().request(m, url, body=body, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content

    async def get(
        self, url: str, /, headers: Optional[Dict[str, bytes]] = None
    ) -> Tuple[int, Dict[str, Any], bytes]:
        metrics["httpclient_requests", ("method", "get")] += 1
        try:
            url = await self.resolve(url)
        except TimeoutError as e:
            return ERR_TIMEOUT, {}, b"Cannot resolve host: %s" % str(e).encode(DEFAULT_ENCODING)
        try:
            r = await super().get(url, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content

    async def post(
        self,
        url: str,
        body: bytes,
        /,
        headers: Optional[Dict[str, bytes]] = None,
    ) -> Tuple[int, Dict[str, Any], bytes]:
        metrics["httpclient_requests", ("method", "post")] += 1
        try:
            url = await self.resolve(url)
        except TimeoutError as e:
            return ERR_TIMEOUT, {}, b"Cannot resolve host: %s" % str(e).encode(DEFAULT_ENCODING)
        try:
            r = await super().post(url, body, headers=headers)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (ConnectionError, HttpError) as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % str(e).encode(DEFAULT_ENCODING)
        except TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        return r.status, r.headers, r.content
