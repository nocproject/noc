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
# Third-party modules
import tornado.gen
import tornado.ioloop
import tornado.iostream
import tornado.httputil
from http_parser.parser import HttpParser
# NOC modules
from noc.core.perf import metrics


DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_REQUEST_TIMEOUT = 3600
DEFAULT_USER_AGENT = "NOC"
DEFAULT_BUFFER_SIZE = 128 * 1024

ERR_TIMEOUT = 599
ERR_READ_TIMEOUT = 598
ERR_PARSE_ERROR = 597


@tornado.gen.coroutine
def fetch(url, method="GET",
          headers=None, body=None,
          connect_timeout=DEFAULT_CONNECT_TIMEOUT,
          request_timeout=DEFAULT_REQUEST_TIMEOUT,
          io_loop=None,
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
    u = urlparse.urlparse(url)
    if ":" in u.netloc:
        host, port = u.netloc.rsplit(":")
        port = int(port)
    else:
        host, port = u.netloc, 80
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        stream = tornado.iostream.IOStream(s, io_loop=io_loop)
        try:
            yield tornado.gen.with_timeout(
                io_loop.time() + connect_timeout,
                future=stream.connect((host, port)),
                io_loop=io_loop
            )
        except tornado.iostream.StreamClosedError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection refused"))
        except tornado.gen.TimeoutError:
            metrics["httpclient_timeouts"] += 1
            raise tornado.gen.Return((ERR_TIMEOUT, {}, "Connection timed out"))
        body = body or ""
        hd = {
            "Host": u.netloc,
            "Connection": "close",
            "User-Agent": DEFAULT_USER_AGENT
        }
        if method == "POST":
            hd["Content-Length"] = str(len(body))
            hd["Content-Type"] = "application/binary"
        if headers:
            hd.update(headers)
        h = tornado.httputil.HTTPHeaders(hd)
        path = u.path
        if u.query:
            path += "?%s" % u.query
        req = "%s %s HTTP/1.1\n%s\n\n%s" % (method, path, h, body)
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
