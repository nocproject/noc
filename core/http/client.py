# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import socket
import urlparse
import threading
# Third-party modules
import tornado.gen
import tornado.ioloop
import tornado.iostream
from http_parser.parser import HttpParser
import cachetools
# NOC modules
from noc.core.perf import metrics
from noc.lib.validators import is_ipv4


DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_REQUEST_TIMEOUT = 3600
DEFAULT_USER_AGENT = "NOC"
DEFAULT_BUFFER_SIZE = 128 * 1024

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
ERR_PARSE_ERROR = 597

NS_CACHE_SIZE = 1000
RESOLVER_TTL = 3

DEFAULT_PORTS = {
    "http": 80,
    "https": 443
}


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
          max_buffer_size=DEFAULT_BUFFER_SIZE):
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
    metrics["httpclient_requests"] += 1
    metrics["httpclient_%s_requests" % method] += 1
    io_loop = io_loop or tornado.ioloop.IOLoop.current()
    u = urlparse.urlparse(str(url))
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        if u.scheme == "https":
            stream = tornado.iostream.SSLIOStream(s, io_loop=io_loop)
        else:
            stream = tornado.iostream.IOStream(s, io_loop=io_loop)
        try:
            yield tornado.gen.with_timeout(
                io_loop.time() + connect_timeout,
                future=stream.connect((addr, port), server_hostname=u.netloc),
                io_loop=io_loop
            )
        except tornado.iostream.StreamClosedError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection refused"))
        except tornado.gen.TimeoutError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection timed out"))
        body = body or ""
        h = {
            "Host": str(u.netloc),
            "Connection": "close",
            "User-Agent": DEFAULT_USER_AGENT
        }
        if method == "POST":
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
        deadline = io_loop.time() + request_timeout
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
        raise tornado.gen.Return((
            parser.get_status_code(),
            parser.get_headers(),
            "".join(response_body)
        ))
    finally:
        s.close()


def fetch_sync(url, method="GET",
               headers=None, body=None,
               connect_timeout=DEFAULT_CONNECT_TIMEOUT,
               request_timeout=DEFAULT_REQUEST_TIMEOUT,
               resolver=resolve,
               max_buffer_size=DEFAULT_BUFFER_SIZE):

    @tornado.gen.coroutine
    def _fetch():
        result = yield fetch(
            url,
            method=method, headers=headers, body=body,
            connect_timeout=connect_timeout,
            request_timeout=request_timeout,
            resolver=resolver,
            max_buffer_size=max_buffer_size
        )
        r.append(result)

    r = []
    ioloop = tornado.ioloop.IOLoop()
    ioloop.run_sync(_fetch)
    return r[0]
