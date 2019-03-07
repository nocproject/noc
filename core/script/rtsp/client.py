# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RTSP Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import socket
import urlparse
import threading
import logging
import struct
# Third-party modules
import tornado.gen
import tornado.ioloop
import tornado.iostream
import cachetools
import six
import ujson
# NOC modules
from noc.core.perf import metrics
from noc.lib.validators import is_ipv4
from noc.config import config

logger = logging.getLogger(__name__)

DEFAULT_CONNECT_TIMEOUT = config.http_client.connect_timeout
DEFAULT_REQUEST_TIMEOUT = config.http_client.request_timeout
DEFAULT_USER_AGENT = config.http_client.user_agent
DEFAULT_BUFFER_SIZE = config.http_client.buffer_size
DEFAULT_MAX_REDIRECTS = config.http_client.max_redirects

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
ERR_PARSE_ERROR = 597

NS_CACHE_SIZE = config.http_client.ns_cache_size
RESOLVER_TTL = config.http_client.resolver_ttl

DEFAULT_PORTS = {
    "rtsp": 554
}

# Methods require Content-Length header
REQUIRE_LENGTH_METHODS = set(["POST", "PUT"])
DEFAULT_PROTOCOL = "RTSP/1.0"

ns_lock = threading.Lock()
ns_cache = cachetools.TTLCache(NS_CACHE_SIZE, ttl=RESOLVER_TTL)


class RTSPParser(object):

    def __init__(self):
        self.is_complete = False
        self.is_partial = True
        self.status_code = 200
        self.headers = {}
        self.body = []
        self.last_data = None

    def is_message_complete(self):
        return self.is_complete

    def execute(self, data, received):
        # print "'%s'" % data
        for line in data.splitlines():
            if line.startswith("RTSP/1.0"):
                _, self.status_code, _ = line.split()
            elif ":" in line:
                self.headers[line.split(":", 1)[0]] = line.split(":", 1)[1].strip()
            else:
                self.is_partial = True
                self.body += [line]
        self.is_complete = True
        return received

    def is_partial_body(self):
        return self.is_partial

    def get_status_code(self):
        return int(self.status_code)

    def get_headers(self):
        return self.headers

    def recv_body(self):
        return "\n".join(self.body)


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
def fetch(url, method="OPTIONS",
          headers=None, body=None,
          connect_timeout=DEFAULT_CONNECT_TIMEOUT,
          request_timeout=DEFAULT_REQUEST_TIMEOUT,
          io_loop=None,
          resolver=resolve,
          max_buffer_size=DEFAULT_BUFFER_SIZE,
          follow_redirects=False,
          max_redirects=DEFAULT_MAX_REDIRECTS,
          validate_cert=config.http_client.validate_certs,
          user=None,
          password=None,
          eof_mark=None
          ):
    """

    :param url: Fetch URL
    :param method: request method "GET", "POST", "PUT" etc
    :param headers: Dict of additional headers
    :param body: Request body for POST and PUT request
    :param connect_timeout:
    :param request_timeout:
    :param io_loop:
    :param resolver:
    :param follow_redirects:
    :param max_redirects:
    :param validate_cert:
    :param user:
    :param password:
    :param max_buffer_size:
    :param eof_mark: Do not consider connection reset as error if
      eof_mark received (string or list)
    :return: code, headers, body
    """
    logger.debug("RTSP %s %s", method, url)
    metrics["rtspclient_requests", ("method", method.lower())] += 1
    # Detect proxy when necessary
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
    # Connect
    stream = None
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        stream = tornado.iostream.IOStream(s, io_loop=io_loop)
        try:
            if isinstance(addr, tuple):
                connect_address = addr
            else:
                connect_address = (addr, port)

            yield tornado.gen.with_timeout(
                io_loop.time() + connect_timeout,
                future=stream.connect(connect_address, server_hostname=u.netloc),
                io_loop=io_loop
            )
        except tornado.iostream.StreamClosedError:
            metrics["rtspclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection refused"))
        except tornado.gen.TimeoutError:
            metrics["rtspclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection timed out"))
        deadline = io_loop.time() + request_timeout
        # Process request
        body = body or ""
        content_type = "application/binary"
        if isinstance(body, unicode):
            body = body.encode("utf-8")
        elif not isinstance(body, six.string_types):
            body = ujson.dumps(body)
            content_type = "text/json"
        h = {
            "Host": str(u.netloc),
            "Connection": "close",
            "User-Agent": DEFAULT_USER_AGENT
        }
        if method in REQUIRE_LENGTH_METHODS:
            h["Content-Length"] = str(len(body))
            h["Content-Type"] = content_type
        if user and password:
            # Include basic auth header
            h["Authorization"] = "Basic %s" % (
                "%s:%s" % (user, password)
            ).encode("base64").strip()
        if headers:
            h.update(headers)
        path = u.path
        if u.query:
            path += "?%s" % u.query
        req = b"%s %s %s\r\n%s\r\n\r\n%s" % (
            method,
            path,
            DEFAULT_PROTOCOL,
            "\r\n".join(b"%s: %s" % (k, h[k]) for k in h),
            body
        )
        try:
            yield tornado.gen.with_timeout(
                deadline,
                future=stream.write(req),
                io_loop=io_loop,
                quiet_exceptions=(tornado.iostream.StreamClosedError,)
            )
        except tornado.iostream.StreamClosedError:
            metrics["rtspclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection reset while sending request"))
        except tornado.gen.TimeoutError:
            metrics["rtspclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Timed out while sending request"))
        parser = RTSPParser()
        response_body = []
        while not parser.is_message_complete():
            try:
                data = yield tornado.gen.with_timeout(
                    deadline,
                    future=stream.read_bytes(max_buffer_size, partial=True),
                    io_loop=io_loop,
                    quiet_exceptions=(tornado.iostream.StreamClosedError,)
                )
            except tornado.iostream.StreamClosedError:
                if not response_body and config.features.pypy:
                    break
                if eof_mark and response_body:
                    # Check if EOF mark is in received data
                    response_body = ["".join(response_body)]
                    if isinstance(eof_mark, six.string_types):
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
                metrics["rtspclient_timeouts"] += 1
                raise tornado.gen.Return((ERR_READ_TIMEOUT, {}, "Connection reset"))
            except tornado.gen.TimeoutError:
                metrics["rtspclient_timeouts"] += 1
                raise tornado.gen.Return((ERR_READ_TIMEOUT, {}, "Request timed out"))
            received = len(data)
            parsed = parser.execute(data, received)
            if parsed != received:
                raise tornado.gen.Return((ERR_PARSE_ERROR, {}, "Parse error"))
            if parser.is_partial_body():
                response_body += [parser.recv_body()]
        code = parser.get_status_code()
        parsed_headers = parser.get_headers()
        logger.debug("RTSP Response %s", code)
        if 300 <= code <= 399 and follow_redirects:
            # Process redirects
            if max_redirects > 0:
                new_url = parsed_headers.get("Location")
                if not new_url:
                    raise tornado.gen.Return((ERR_PARSE_ERROR, {}, "No Location header"))
                logger.debug("RTSP redirect %s %s", code, new_url)
                code, parsed_headers, response_body = yield fetch(
                    new_url,
                    method="OPTIONS", headers=headers,
                    connect_timeout=connect_timeout,
                    request_timeout=request_timeout,
                    resolver=resolver,
                    max_buffer_size=max_buffer_size,
                    follow_redirects=follow_redirects,
                    max_redirects=max_redirects - 1,
                    validate_cert=validate_cert
                )
                raise tornado.gen.Return((code, parsed_headers, response_body))
            else:
                raise tornado.gen.Return((404, {}, "Redirect limit exceeded"))
        # @todo: Process gzip and deflate Content-Encoding
        raise tornado.gen.Return((
            code,
            parsed_headers,
            "".join(response_body)
        ))
    finally:
        if stream:
            stream.close()
        else:
            s.close()


def fetch_sync(url, method="OPTIONS",
               headers=None, body=None,
               connect_timeout=DEFAULT_CONNECT_TIMEOUT,
               request_timeout=DEFAULT_REQUEST_TIMEOUT,
               resolver=resolve,
               max_buffer_size=DEFAULT_BUFFER_SIZE,
               follow_redirects=False,
               max_redirects=DEFAULT_MAX_REDIRECTS,
               validate_cert=config.http_client.validate_certs,
               user=None,
               password=None,
               eof_mark=None):

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
            user=user,
            password=password,
            eof_mark=eof_mark
        )
        r.append(result)

    r = []
    ioloop = tornado.ioloop.IOLoop()
    ioloop.run_sync(_fetch)
    return r[0]


def to32u(n):
    return struct.pack("<L", n)
