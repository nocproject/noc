# ----------------------------------------------------------------------
# HTTP Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
import threading
import ssl
import logging
import zlib
import time
import struct
import codecs
from urllib.parse import urlparse
import asyncio
import random

# Third-party modules
import cachetools
import orjson
from gufo.http import BasicAuth, RequestMethod, DEFLATE, GZIP
from gufo.http.async_client import AsyncClient
from gufo.http.sync_client import SyncClient as HttpClientSync
from typing import Optional, List, Tuple, Any, Dict

# NOC modules
from noc.core.perf import metrics
from noc.core.validators import is_ipv4
from .proxy import SYSTEM_PROXIES
from noc.config import config
from noc.core.comp import smart_bytes, smart_text

logger = logging.getLogger(__name__)

DEFAULT_CONNECT_TIMEOUT = config.http_client.connect_timeout
DEFAULT_REQUEST_TIMEOUT = config.http_client.request_timeout
DEFAULT_USER_AGENT = config.http_client.user_agent
DEFAULT_BUFFER_SIZE = config.http_client.buffer_size
DEFAULT_MAX_REDIRECTS = config.http_client.max_redirects

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
ERR_PARSE_ERROR = 597

DEFAULT_PORTS = {"http": config.http_client.http_port, "https": config.http_client.https_port}

# Methods require Content-Length header
REQUIRE_LENGTH_METHODS = {"POST", "PUT"}

ns_lock = threading.Lock()
ns_cache = cachetools.TTLCache(
    config.http_client.ns_cache_size, ttl=config.http_client.resolver_ttl
)

CE_DEFLATE = "deflate"
CE_GZIP = "gzip"

gufo_encoding_map = {CE_DEFLATE: DEFLATE, CE_GZIP: GZIP}


async def resolve(host):
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


async def fetch(
    url: str,
    method: str = "GET",
    headers=None,
    body: Optional[bytes] = None,
    connect_timeout=DEFAULT_CONNECT_TIMEOUT,
    request_timeout=DEFAULT_REQUEST_TIMEOUT,
    resolver=resolve,
    max_buffer_size=DEFAULT_BUFFER_SIZE,
    follow_redirects: bool = False,
    max_redirects=DEFAULT_MAX_REDIRECTS,
    validate_cert=config.http_client.validate_certs,
    allow_proxy: bool = False,
    proxies=None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    content_encoding: Optional[str] = None,
    eof_mark: Optional[bytes] = None,
) -> Tuple[int, Dict[str, Any], bytes]:
    """

    :param url: Fetch URL
    :param method: request method "GET", "POST", "PUT" etc
    :param headers: Dict of additional headers
    :param body: Request body for POST and PUT request
    :param connect_timeout:
    :param request_timeout:
    :param resolver:
    :param follow_redirects:
    :param max_redirects:
    :param validate_cert:
    :param allow_proxy:
    :param proxies:
    :param user:
    :param password:
    :param max_buffer_size:
    :param content_encoding:
    :param eof_mark: Do not consider connection reset as error if
      eof_mark received (string or list)
    :return: code, headers, body
    """
    params = {
        "max_redirects": max_redirects if follow_redirects else 0,
        "validate_cert": validate_cert,
        "connect_timeout": connect_timeout,
        "timeout": request_timeout,
        "headers": headers,
        "user_agent": DEFAULT_USER_AGENT,
        "compression": gufo_encoding_map.get(content_encoding),
        "auth": BasicAuth(user=user, password=password) if user else None,
    }
    body = body or ""
    content_type = b"application/binary"
    if not isinstance(body, (str, bytes)):
        body = smart_text(orjson.dumps(body))
        content_type = b"application/json"
    body = smart_bytes(body)  # Here and below body is binary
    h = {"Connection": b"close", "Content-Type": content_type}
    async with AsyncClient(**params) as client:
        try:
            method = RequestMethod[method]
        except ValueError:
            raise NotImplementedError("Not implementer method: %s", method)
        r = client.request(RequestMethod(method), url, body=body)
        return r.status, {}, r.read()


async def __fetch(
    url: str,
    method: str = "GET",
    headers=None,
    body: Optional[bytes] = None,
    connect_timeout=DEFAULT_CONNECT_TIMEOUT,
    request_timeout=DEFAULT_REQUEST_TIMEOUT,
    resolver=resolve,
    max_buffer_size=DEFAULT_BUFFER_SIZE,
    follow_redirects: bool = False,
    max_redirects=DEFAULT_MAX_REDIRECTS,
    validate_cert=config.http_client.validate_certs,
    allow_proxy: bool = False,
    proxies=None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    content_encoding: Optional[str] = None,
    eof_mark: Optional[bytes] = None,
) -> Tuple[int, Dict[str, Any], bytes]:
    """

    :param url: Fetch URL
    :param method: request method "GET", "POST", "PUT" etc
    :param headers: Dict of additional headers
    :param body: Request body for POST and PUT request
    :param connect_timeout:
    :param request_timeout:
    :param resolver:
    :param follow_redirects:
    :param max_redirects:
    :param validate_cert:
    :param allow_proxy:
    :param proxies:
    :param user:
    :param password:
    :param max_buffer_size:
    :param content_encoding:
    :param eof_mark: Do not consider connection reset as error if
      eof_mark received (string or list)
    :return: code, headers, body
    """

    def get_connect_options():
        opts = {}
        if use_tls and not proxy:
            ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            if validate_cert:
                ctx.check_hostname = True
                ctx.verify_mode = ssl.CERT_REQUIRED
            else:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            opts["ssl"] = ctx
        return opts

    metrics["httpclient_requests", ("method", method.lower())] += 1
    #
    if eof_mark:
        eof_mark = smart_bytes(eof_mark)
    # Detect proxy when necessary
    u = urlparse(str(url))
    use_tls = u.scheme == "https"
    proto = "HTTPS" if use_tls else "HTTP"
    logger.debug("%s %s %s", proto, method, url)
    if ":" in u.netloc:
        host, port = u.netloc.rsplit(":")
        port = int(port)
    else:
        host = u.netloc
        port = DEFAULT_PORTS.get(u.scheme)
        if not port:
            return ERR_TIMEOUT, {}, b"Cannot resolve port for scheme: %s" % smart_bytes(u.scheme)
    if is_ipv4(host):
        addr = host
    else:
        addr = await resolver(host)
    if not addr:
        return ERR_TIMEOUT, {}, "Cannot resolve host: %s" % host
    # Detect proxy server
    if allow_proxy:
        proxy = (proxies or SYSTEM_PROXIES).get(u.scheme)
    else:
        proxy = None
    # Connect
    reader, writer = None, None
    if proxy:
        connect_address = proxy
    elif isinstance(addr, tuple):
        connect_address = addr
    else:
        connect_address = (addr, port)
    try:
        try:
            if proxy:
                logger.debug("Connecting to proxy %s:%s", connect_address[0], connect_address[1])
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(
                    connect_address[0], connect_address[1], **get_connect_options()
                ),
                connect_timeout,
            )
        except ConnectionRefusedError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection refused"
        except OSError as e:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection error: %s" % smart_bytes(e)
        except asyncio.TimeoutError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection timed out"
        # Proxy CONNECT
        if proxy:
            logger.debug("Sending CONNECT %s:%s", addr, port)
            # Send CONNECT request
            req = b"CONNECT %s:%s HTTP/1.1\r\nUser-Agent: %s\r\n\r\n" % (
                smart_bytes(addr),
                smart_bytes(port),
                smart_bytes(DEFAULT_USER_AGENT),
            )
            writer.write(smart_bytes(req))
            try:
                await asyncio.wait_for(writer.drain(), request_timeout)
            except (asyncio.TimeoutError, TimeoutError):
                metrics["httpclient_proxy_timeouts"] += 1
                return ERR_TIMEOUT, {}, b"Timed out while sending request to proxy"
            # Wait for proxy response
            parser = None
            while not parser.is_headers_complete():
                try:
                    data = await asyncio.wait_for(reader.read(max_buffer_size), request_timeout)
                except (asyncio.TimeoutError, TimeoutError):
                    metrics["httpclient_proxy_timeouts"] += 1
                    return ERR_TIMEOUT, {}, b"Timed out while sending request to proxy"
                received = len(data)
                parsed = parser.execute(data, received)
                if parsed != received:
                    return ERR_PARSE_ERROR, {}, b"Parse error"
            code = parser.get_status_code()
            logger.debug("Proxy response: %s", code)
            if not 200 <= code <= 299:
                return code, parser.get_headers(), "Proxy error: %s" % code
        # Process request
        body = body or ""
        content_type = "application/binary"
        if not isinstance(body, (str, bytes)):
            body = smart_text(orjson.dumps(body))
            content_type = "application/json"
        body = smart_bytes(body)  # Here and below body is binary
        h = {"Host": str(u.netloc), "Connection": "close", "User-Agent": DEFAULT_USER_AGENT}
        if body and content_encoding:
            if content_encoding == CE_DEFLATE:
                # Deflate compression
                h["Content-Encoding"] = CE_DEFLATE
                compress = zlib.compressobj(
                    zlib.Z_DEFAULT_COMPRESSION,
                    zlib.DEFLATED,
                    -zlib.MAX_WBITS,
                    zlib.DEF_MEM_LEVEL,
                    zlib.Z_DEFAULT_STRATEGY,
                )
                body = compress.compress(body) + compress.flush()
            elif content_encoding == CE_GZIP:
                # gzip compression
                h["Content-Encoding"] = CE_GZIP
                compress = zlib.compressobj(
                    6, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, 0
                )
                crc = zlib.crc32(body, 0) & 0xFFFFFFFF
                body = b"\x1f\x8b\x08\x00%s\x02\xff%s%s%s%s" % (
                    to32u(int(time.time())),
                    compress.compress(body),
                    compress.flush(),
                    to32u(crc),
                    to32u(len(body)),
                )
        if method in REQUIRE_LENGTH_METHODS:
            h["Content-Length"] = str(len(body))
            h["Content-Type"] = content_type
        if user and password:
            # Include basic auth header
            uh = smart_text("%s:%s" % (user, password))
            h["Authorization"] = b"Basic %s" % codecs.encode(uh.encode("utf-8"), "base64").strip()
        if headers:
            h.update(headers)
        path = u.path
        if u.query:
            path += "?%s" % u.query
        req = b"%s %s HTTP/1.1\r\n%s\r\n\r\n%s" % (
            smart_bytes(method),
            smart_bytes(path),
            b"\r\n".join(b"%s: %s" % (smart_bytes(k), smart_bytes(h[k])) for k in h),
            body,
        )
        try:
            writer.write(req)
            await asyncio.wait_for(writer.drain(), request_timeout)
        except ConnectionResetError:
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Connection reset while sending request"
        except (asyncio.TimeoutError, TimeoutError):
            metrics["httpclient_timeouts"] += 1
            return ERR_TIMEOUT, {}, b"Timed out while sending request"
        parser = None
        response_body: List[bytes] = []
        while not parser.is_message_complete():
            try:
                data = await asyncio.wait_for(reader.read(max_buffer_size), request_timeout)
                is_eof = not data
            except (asyncio.IncompleteReadError, ConnectionResetError):
                is_eof = True
            except (asyncio.TimeoutError, TimeoutError):
                metrics["httpclient_timeouts"] += 1
                return ERR_READ_TIMEOUT, {}, b"Request timed out"
            if is_eof:
                if eof_mark and response_body:
                    # Check if EOF mark is in received data
                    response_body = [b"".join(response_body)]
                    if isinstance(eof_mark, str):
                        if eof_mark in response_body[0]:
                            break
                    else:
                        found = False
                        for m in eof_mark:
                            if m in response_body[0]:
                                found = True
                                break
                        if found:
                            break
                metrics["httpclient_timeouts"] += 1
                return ERR_READ_TIMEOUT, {}, b"Connection reset"
            received = len(data)
            parsed = parser.execute(data, received)
            if parsed != received:
                return ERR_PARSE_ERROR, {}, b"Parse error"
            if parser.is_partial_body():
                response_body += [parser.recv_body()]
        code = parser.get_status_code()
        parsed_headers = parser.get_headers()
        logger.debug("HTTP Response %s", code)
        if 300 <= code <= 399 and follow_redirects:
            # Process redirects
            if max_redirects > 0:
                new_url = parsed_headers.get("Location")
                if not new_url:
                    return ERR_PARSE_ERROR, {}, b"No Location header"
                logger.debug("HTTP redirect %s %s", code, new_url)
                return await fetch(
                    new_url,
                    method="GET",
                    headers=headers,
                    connect_timeout=connect_timeout,
                    request_timeout=request_timeout,
                    resolver=resolver,
                    max_buffer_size=max_buffer_size,
                    follow_redirects=follow_redirects,
                    max_redirects=max_redirects - 1,
                    validate_cert=validate_cert,
                    allow_proxy=allow_proxy,
                    proxies=proxies,
                )
            else:
                return 404, {}, b"Redirect limit exceeded"
        # @todo: Process gzip and deflate Content-Encoding
        return code, parsed_headers, b"".join(response_body)
    finally:
        if writer:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionResetError:
                pass


def fetch_sync(
    url: str,
    method: str = "GET",
    headers=None,
    body: Optional[bytes] = None,
    connect_timeout=DEFAULT_CONNECT_TIMEOUT,
    request_timeout=DEFAULT_REQUEST_TIMEOUT,
    resolver=resolve,
    max_buffer_size=DEFAULT_BUFFER_SIZE,
    follow_redirects=False,
    max_redirects=DEFAULT_MAX_REDIRECTS,
    validate_cert=config.http_client.validate_certs,
    allow_proxy: bool = False,
    proxies=None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    content_encoding: Optional[str] = None,
    eof_mark: Optional[bytes] = None,
) -> Tuple[int, Dict[str, Any], bytes]:
    params = {
        "max_redirects": max_redirects if follow_redirects else 0,
        "validate_cert": validate_cert,
        "connect_timeout": connect_timeout,
        "timeout": request_timeout,
        "headers": headers,
        "compression": gufo_encoding_map.get(content_encoding),
        "user_agent": DEFAULT_USER_AGENT,
        "auth": BasicAuth(user=user, password=password) if user else None,
    }
    body = body or ""
    content_type = b"application/binary"
    if not isinstance(body, (str, bytes)):
        body = smart_text(orjson.dumps(body))
        content_type = b"application/json"
    body = smart_bytes(body)  # Here and below body is binary
    h = {"Connection": b"close", "Content-Type": content_type}
    if headers:
        h.update({k: smart_bytes(v) for k, v in headers.items()})
    with HttpClientSync(**params) as client:
        try:
            method = RequestMethod[method]
        except ValueError:
            raise NotImplementedError("Not implementer method: %s", method)
        r = client.request(RequestMethod(method), url, body=body, headers=h)
        return r.status, {}, r.read()


def to32u(n):
    return struct.pack("<L", n)
