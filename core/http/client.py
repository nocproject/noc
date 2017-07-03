# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import socket
import urlparse
import threading
import ssl
import logging
# Third-party modules
import tornado.gen
import tornado.ioloop
import tornado.iostream
from http_parser.parser import HttpParser
import cachetools
# NOC modules
from noc.core.perf import metrics
from noc.lib.validators import is_ipv4

logger = logging.getLogger(__name__)

DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_REQUEST_TIMEOUT = 3600
DEFAULT_USER_AGENT = "NOC"
DEFAULT_BUFFER_SIZE = 128 * 1024
DEFAULT_MAX_REDIRECTS = 5

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
ERR_PARSE_ERROR = 597

NS_CACHE_SIZE = 1000
RESOLVER_TTL = 3

DEFAULT_PORTS = {
    "http": 80,
    "https": 443
}

SYSTEM_PROXIES = {}

# Methods require Content-Length header
REQUIRE_LENGTH_METHODS = set(["POST", "PUT"])

ns_lock = threading.Lock()
ns_cache = cachetools.TTLCache(NS_CACHE_SIZE, ttl=RESOLVER_TTL)


@tornado.gen.coroutine
def resolve(host):
    """
    Resolve host and return address
    :param host:
    :return:
    """
    with ns_lock:
        addr = ns_cache.get(host)
    if addr:
        raise tornado.gen.Return(addr)
    try:
        addr = socket.gethostbyname(host)
        with ns_lock:
            ns_cache[host] = addr
        raise tornado.gen.Return(addr)
    except socket.gaierror:
        return None


@tornado.gen.coroutine
def fetch(url, method="GET",
          headers=None, body=None,
          connect_timeout=DEFAULT_CONNECT_TIMEOUT,
          request_timeout=DEFAULT_REQUEST_TIMEOUT,
          io_loop=None,
          resolver=resolve,
          max_buffer_size=DEFAULT_BUFFER_SIZE,
          follow_redirects=False,
          max_redirects=DEFAULT_MAX_REDIRECTS,
          validate_cert=False,
          allow_proxy=False,
          proxies=None
    ):
    """

    :param url:
    :param method:
    :param headers:
    :param body:
    :param connect_timeout:
    :param request_timeout:
    :param ioloop:
    :param max_buffer_size:
    :return: code, headers, body
    """
    def get_ssl_options():
        ssl_options = {}
        if validate_cert:
            ssl_options["cert_reqs"] = ssl.CERT_REQUIRED
        return ssl_options

    logger.debug("HTTP %s %s", method, url)
    metrics["httpclient_requests"] += 1
    metrics["httpclient_%s_requests" % method] += 1
    # Detect proxy when necessary
    io_loop = io_loop or tornado.ioloop.IOLoop.current()
    u = urlparse.urlparse(str(url))
    use_tls = u.scheme == "https"
    if ":" in u.netloc:
        host, port = u.netloc.rsplit(":")
        port = int(port)
    else:
        host = u.netloc
        port = DEFAULT_PORTS.get(u.scheme)
        if not port:
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Cannot resolve port for scheme: %s" % u.scheme))
    if is_ipv4(host):
        addr = host
    else:
        addr = yield resolver(host)
    if not addr:
        raise tornado.gen.Return((ERR_TIMEOUT, {}, "Cannot resolve host: %s" % host))
    # Detect proxy server
    if allow_proxy:
        proxy = (proxies or SYSTEM_PROXIES).get(u.scheme)
    else:
        proxy = None
    # Connect
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if use_tls and not proxy:
            stream = tornado.iostream.SSLIOStream(
                s, io_loop=io_loop, ssl_options=get_ssl_options()
            )
        else:
            stream = tornado.iostream.IOStream(s, io_loop=io_loop)
        try:
            if proxy:
                connect_address = proxy
            else:
                connect_address = (addr, port)

            if proxy:
                logger.debug("Connecting to proxy %s:%s",
                             connect_address[0], connect_address[1])
            yield tornado.gen.with_timeout(
                io_loop.time() + connect_timeout,
                future=stream.connect(connect_address, server_hostname=u.netloc),
                io_loop=io_loop
            )
        except tornado.iostream.StreamClosedError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection refused"))
        except tornado.gen.TimeoutError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection timed out"))
        deadline = io_loop.time() + request_timeout
        # Proxy CONNECT
        if proxy:
            logger.debug("Sending CONNECT %s:%s", addr, port)
            # Send CONNECT request
            req = b"CONNECT %s:%s HTTP/1.1\r\nUser-Agent: %s\r\n\r\n" % (
                addr, port, DEFAULT_USER_AGENT
            )
            try:
                yield tornado.gen.with_timeout(
                    deadline,
                    future=stream.write(req),
                    io_loop=io_loop
                )
            except tornado.iostream.StreamClosedError:
                metrics["httpclient_proxy_timeouts"] += 1
                raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection reset while connecting to proxy"))
            except tornado.gen.TimeoutError:
                metrics["httpclient_proxy_timeouts"] += 1
                raise tornado.gen.Return((ERR_TIMEOUT, {}, "Timed out while sending request to proxy"))
            # Wait for proxy response
            parser = HttpParser()
            while not parser.is_headers_complete():
                try:
                    data = yield tornado.gen.with_timeout(
                        deadline,
                        future=stream.read_bytes(max_buffer_size, partial=True),
                        io_loop=io_loop
                    )
                except tornado.iostream.StreamClosedError:
                    metrics["httpclient_proxy_timeouts"] += 1
                    raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection reset while connecting to proxy"))
                except tornado.gen.TimeoutError:
                    metrics["httpclient_proxy_timeouts"] += 1
                    raise tornado.gen.Return((ERR_TIMEOUT, {}, "Timed out while sending request to proxy"))
                received = len(data)
                parsed = parser.execute(data, received)
                if parsed != received:
                    raise tornado.gen.Return((ERR_PARSE_ERROR, {}, "Parse error"))
            code = parser.get_status_code()
            logger.debug("Proxy response: %s", code)
            if not (200 <= code <= 299):
                raise tornado.gen.Return((code, parser.get_headers(), "Proxy error: %s" % code))
            # Switch to TLS when necessary
            if use_tls:
                logger.debug("Starting TLS negotiation")
                try:
                    stream = yield tornado.gen.with_timeout(
                        deadline,
                        future=stream.start_tls(
                            server_side=False,
                            ssl_options=get_ssl_options(),
                            server_hostname=u.netloc
                        ),
                        io_loop=io_loop
                    )
                except tornado.iostream.StreamClosedError:
                    metrics["httpclient_proxy_timeouts"] += 1
                    raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection reset while connecting to proxy"))
                except tornado.gen.TimeoutError:
                    metrics["httpclient_proxy_timeouts"] += 1
                    raise tornado.gen.Return((ERR_TIMEOUT, {}, "Timed out while sending request to proxy"))
        # Process request
        body = body or ""
        if isinstance(body, unicode):
            body = body.encode("utf-8")
        h = {
            "Host": str(u.netloc),
            "Connection": "close",
            "User-Agent": DEFAULT_USER_AGENT
        }
        if method in REQUIRE_LENGTH_METHODS:
            h["Content-Length"] = str(len(body))
            h["Content-Type"] = "application/binary"
        if headers:
            h.update(headers)
        path = u.path
        if u.query:
            path += "?%s" % u.query
        req = b"%s %s HTTP/1.1\r\n%s\r\n\r\n%s" % (
            method,
            path,
            "\r\n".join(b"%s: %s" % (k, h[k]) for k in h),
            body
        )
        try:
            yield tornado.gen.with_timeout(
                deadline,
                future=stream.write(req),
                io_loop=io_loop
            )
        except tornado.iostream.StreamClosedError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection reset while sending request"))
        except tornado.gen.TimeoutError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Timed out while sending request"))
        parser = HttpParser()
        response_body = []
        while not parser.is_message_complete():
            try:
                data = yield tornado.gen.with_timeout(
                    deadline,
                    future=stream.read_bytes(max_buffer_size, partial=True),
                    io_loop=io_loop
                )
            except tornado.iostream.StreamClosedError:
                metrics["httpclient_timeouts"] += 1
                raise tornado.gen.Return((ERR_READ_TIMEOUT, {}, "Connection reset"))
            except tornado.gen.TimeoutError:
                metrics["httpclient_timeouts"] += 1
                raise tornado.gen.Return((ERR_READ_TIMEOUT, {}, "Request timed out"))
            received = len(data)
            parsed = parser.execute(data, received)
            if parsed != received:
                raise tornado.gen.Return((ERR_PARSE_ERROR, {}, "Parse error"))
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
                    raise tornado.gen.Return((ERR_PARSE_ERROR, {}, "No Location header"))
                logger.debug("HTTP redirect %s %s", code, new_url)
                code, parsed_headers, response_body = yield fetch(
                    new_url,
                    method="GET", headers=headers,
                    connect_timeout=connect_timeout,
                    request_timeout=request_timeout,
                    resolver=resolver,
                    max_buffer_size=max_buffer_size,
                    follow_redirects=follow_redirects,
                    max_redirects=max_redirects - 1,
                    validate_cert=validate_cert,
                    allow_proxy=allow_proxy,
                    proxies=proxies
                )
                raise tornado.gen.Return((code, parsed_headers, response_body))
            else:
                raise tornado.gen.Return((404, {}, "Redirect limit exceeded"))
        raise tornado.gen.Return((
            code,
            parsed_headers,
            "".join(response_body)
        ))
    finally:
        s.close()


def fetch_sync(url, method="GET",
               headers=None, body=None,
               connect_timeout=DEFAULT_CONNECT_TIMEOUT,
               request_timeout=DEFAULT_REQUEST_TIMEOUT,
               resolver=resolve,
               max_buffer_size=DEFAULT_BUFFER_SIZE,
               follow_redirects=False,
               max_redirects=DEFAULT_MAX_REDIRECTS,
               validate_cert=False,
               allow_proxy=False,
               proxies=None):

    @tornado.gen.coroutine
    def _fetch():
        result = yield fetch(
            url,
            method=method, headers=headers, body=body,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout,
            resolver=resolver,
            max_buffer_size=max_buffer_size,
            follow_redirects=follow_redirects,
            max_redirects=max_redirects,
            validate_cert=validate_cert,
            allow_proxy=allow_proxy,
            proxies=proxies
        )
        r.append(result)

    r = []
    ioloop = tornado.ioloop.IOLoop()
    ioloop.run_sync(_fetch)
    return r[0]


def setup_proxies():
    def get_addr(a):
        aa = a.split("://", 1)[1]
        if aa.endswith("/"):
            aa = aa[:-1]
        host, port = aa.split(":")
        return host, int(port)

    http_proxy = os.environ.get("http_proxy")
    if http_proxy:
        SYSTEM_PROXIES["http"] = get_addr(http_proxy)
    https_proxy = os.environ.get("https_proxy")
    if https_proxy:
        SYSTEM_PROXIES["https"] = get_addr(https_proxy)
    if not SYSTEM_PROXIES:
        logger.debug("No proxy servers configures")
    else:
        logger.debug("Using proxy servers: %s",
                     ", ".join("%s = %s" % (
                         k, SYSTEM_PROXIES[k]
                     ) for k in sorted(SYSTEM_PROXIES)))

setup_proxies()
