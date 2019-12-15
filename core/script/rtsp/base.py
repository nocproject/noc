# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RTSP class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import socket
import datetime
import os

# Third-party modules
from six.moves.urllib.request import parse_http_list, parse_keqv_list
import tornado.ioloop
import tornado.iostream
import tornado.gen
import hashlib

# NOC modules
from noc.config import config
from noc.core.log import PrefixLoggerAdapter
from noc.core.comp import smart_bytes
from noc.core.span import Span
from ..cli.telnet import TelnetIOStream
from .error import RTSPConnectionRefused, RTSPAuthFailed, RTSPBadResponse, RTSPError

DEFAULT_PROTOCOL = "RTSP/1.0"
DEFAULT_USER_AGENT = config.http_client.user_agent
MULTIPLE_HEADER = {"WWW-Authenticate"}


class RTSPBase(object):
    name = "rtsp"
    iostream_class = TelnetIOStream
    default_port = 554
    BUFFER_SIZE = config.activator.buffer_size
    MATCH_TAIL = 256
    # Retries on immediate disconnect
    CONNECT_RETRIES = config.activator.connect_retries
    # Timeout after immediate disconnect
    CONNECT_TIMEOUT = config.activator.connect_timeout
    # compiled capabilities
    HAS_TCP_KEEPALIVE = hasattr(socket, "SO_KEEPALIVE")
    HAS_TCP_KEEPIDLE = hasattr(socket, "TCP_KEEPIDLE")
    HAS_TCP_KEEPINTVL = hasattr(socket, "TCP_KEEPINTVL")
    HAS_TCP_KEEPCNT = hasattr(socket, "TCP_KEEPCNT")
    HAS_TCP_NODELAY = hasattr(socket, "TCP_NODELAY")
    # Time until sending first keepalive probe
    KEEP_IDLE = 10
    # Keepalive packets interval
    KEEP_INTVL = 10
    # Terminate connection after N keepalive failures
    KEEP_CNT = 3

    def __init__(self, script, tos=None):
        self.script = script
        self.profile = script.profile
        self.logger = PrefixLoggerAdapter(self.script.logger, self.name)
        self.iostream = None
        self.ioloop = None
        self.path = None
        self.cseq = 1
        self.method = None
        self.headers = None
        self.auth = None
        self.buffer = ""
        self.is_started = False
        self.result = None
        self.error = None
        self.is_closed = False
        self.close_timeout = None
        self.current_timeout = None
        self.tos = tos
        self.rx_rtsp_end = "\r\n\r\n"

    def close(self):
        self.script.close_current_session()
        self.close_iostream()
        if self.ioloop:
            self.logger.debug("Closing IOLoop")
            self.ioloop.close(all_fds=True)
            self.ioloop = None
        self.is_closed = True

    def close_iostream(self):
        if self.iostream:
            self.iostream.close()

    def deferred_close(self, session_timeout):
        if self.is_closed or not self.iostream:
            return
        self.logger.debug("Setting close timeout to %ss", session_timeout)
        # Cannot call call_later directly due to
        # thread-safety problems
        # See tornado issue #1773
        tornado.ioloop.IOLoop.instance().add_callback(self._set_close_timeout, session_timeout)

    def _set_close_timeout(self, session_timeout):
        """
        Wrapper to deal with IOLoop.add_timeout thread safety problem
        :param session_timeout:
        :return:
        """
        self.close_timeout = tornado.ioloop.IOLoop.instance().call_later(
            session_timeout, self.close
        )

    def create_iostream(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.tos:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, self.tos)
        if self.HAS_TCP_NODELAY:
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if self.HAS_TCP_KEEPALIVE:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if self.HAS_TCP_KEEPIDLE:
                s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, self.KEEP_IDLE)
            if self.HAS_TCP_KEEPINTVL:
                s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, self.KEEP_INTVL)
            if self.HAS_TCP_KEEPCNT:
                s.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, self.KEEP_CNT)
        return self.iostream_class(s, self)

    def set_timeout(self, timeout):
        if timeout:
            self.logger.debug("Setting timeout: %ss", timeout)
            self.current_timeout = datetime.timedelta(seconds=timeout)
        else:
            if self.current_timeout:
                self.logger.debug("Resetting timeouts")
            self.current_timeout = None

    def set_script(self, script):
        self.script = script
        if self.close_timeout:
            tornado.ioloop.IOLoop.instance().remove_timeout(self.close_timeout)
            self.close_timeout = None

    def get_uri(self, port=None):
        address = self.script.credentials.get("address")
        if not port:
            port = self.default_port
        if port:
            address += ":%s" % port
        uri = "rtsp://%s%s" % (address, self.path)
        return uri.encode("utf-8")

    @tornado.gen.coroutine
    def send(self, method=None, body=None):
        # @todo: Apply encoding
        self.error = None
        body = body or ""
        method = method or self.method
        h = {
            # "Host": str(u.netloc),
            # "Connection": "close",
            "CSeq": self.cseq,
            "User-Agent": DEFAULT_USER_AGENT,
        }
        if self.auth:
            h["Authorization"] = self.auth.build_digest_header(
                self.get_uri(), method, self.headers["WWW-Authenticate"]["Digest"]
            )
        req = b"%s %s %s\r\n%s\r\n\r\n%s" % (
            method,
            self.get_uri(),
            DEFAULT_PROTOCOL,
            "\r\n".join(b"%s: %s" % (k, h[k]) for k in h),
            body,
        )

        self.logger.debug("Send: %r", req)
        yield self.iostream.write(req)
        self.cseq += 1

    @tornado.gen.coroutine
    def submit(self):
        # Create iostream and connect, when necessary
        if not self.iostream:
            self.iostream = self.create_iostream()
            address = (self.script.credentials.get("address"), self.default_port)
            self.logger.debug("Connecting %s", address)
            try:
                yield self.iostream.connect(address)
            except tornado.iostream.StreamClosedError:
                self.logger.debug("Connection refused")
                self.error = RTSPConnectionRefused("Connection refused")
                raise tornado.gen.Return(None)
            self.logger.debug("Connected")
            yield self.iostream.startup()
        # Perform all necessary login procedures
        if not self.is_started:
            self.is_started = True
            yield self.send("OPTIONS")
            yield self.get_rtsp_response()
            if self.error and self.error.code == 401:
                self.logger.info("Authentication needed")
                self.auth = DigestAuth(
                    user=self.script.credentials.get("user"),
                    password=self.script.credentials.get("password"),
                )
                # Send command
        yield self.send()
        r = yield self.get_rtsp_response()
        raise tornado.gen.Return(r)

    @tornado.gen.coroutine
    def get_rtsp_response(self):
        result = []
        header_sep = "\r\n\r\n"
        while True:
            r = yield self.read_until_end()
            # r = r.strip()
            # Process header
            if header_sep not in r:
                self.result = ""
                self.error = RTSPBadResponse("Missed header separator")
                raise tornado.gen.Return(None)
            header, r = r.split(header_sep, 1)
            code, msg, headers = self.parse_rtsp_header(header)
            self.headers = headers
            self.logger.debug(
                "Parsed received, err code: %d, err message: %s, headers: %s", code, msg, headers
            )
            if code == 401:
                self.result = ""
                self.error = RTSPAuthFailed("%s (code=%s)" % (msg, code), code=int(code))
                raise tornado.gen.Return(None)
            if not 200 <= code <= 299:
                # RTSP Error
                self.result = ""
                self.error = RTSPError("%s (code=%s)" % (msg, code), code=int(code))
                raise tornado.gen.Return(None)
            result += [r]
            break
        self.result = "".join(result)
        raise tornado.gen.Return(self.result)

    @staticmethod
    def parse_rtsp_header(data):
        code, msg, headers = 200, "", {}
        for line in data.splitlines():
            if line.startswith("RTSP/1.0"):
                _, code, msg = line.split(None, 2)
            elif ":" in line:
                h, v = line.split(":", 1)
                if h in MULTIPLE_HEADER:
                    if h not in headers:
                        headers[h] = {}
                    auth, line = v.split(None, 1)
                    items = parse_http_list(line)
                    headers[h][auth] = parse_keqv_list(items)
                    continue
                headers[h] = v.strip()
        return int(code), msg, headers

    def execute(self, path, method, **kwargs):
        """
        Perform request and return result
        :param path:
        :param method:
        :param kwargs:
        :return:
        """
        if self.close_timeout:
            self.logger.debug("Removing close timeout")
            self.ioloop.remove_timeout(self.close_timeout)
            self.close_timeout = None
        self.buffer = ""
        # self.command = self.profile.get_mml_command(cmd, **kwargs)
        self.path = path
        self.method = method
        self.error = None
        if not self.ioloop:
            self.logger.debug("Creating IOLoop")
            self.ioloop = tornado.ioloop.IOLoop()
        with Span(
            server=self.script.credentials.get("address"), service=self.name, in_label=self.method
        ) as s:
            self.ioloop.run_sync(self.submit)
            if self.error:
                if s:
                    s.error_text = str(self.error)
                raise self.error
            else:
                return self.result

    @tornado.gen.coroutine
    def read_until_end(self):
        connect_retries = self.CONNECT_RETRIES
        while True:
            try:
                f = self.iostream.read_bytes(self.BUFFER_SIZE, partial=True)
                if self.current_timeout:
                    r = yield tornado.gen.with_timeout(self.current_timeout, f)
                else:
                    r = yield f
            except tornado.iostream.StreamClosedError:
                # Check if remote end closes connection just
                # after connection established
                if not self.is_started and connect_retries:
                    self.logger.info(
                        "Connection reset. %d retries left. Waiting %d seconds",
                        connect_retries,
                        self.CONNECT_TIMEOUT,
                    )
                    while connect_retries:
                        yield tornado.gen.sleep(self.CONNECT_TIMEOUT)
                        connect_retries -= 1
                        self.iostream = self.create_iostream()
                        address = (
                            self.script.credentials.get("address"),
                            self.script.credentials.get("cli_port", self.default_port),
                        )
                        self.logger.debug("Connecting %s", address)
                        try:
                            yield self.iostream.connect(address)
                            break
                        except tornado.iostream.StreamClosedError:
                            if not connect_retries:
                                raise tornado.iostream.StreamClosedError()
                    continue
                else:
                    raise tornado.iostream.StreamClosedError()
            except tornado.gen.TimeoutError:
                self.logger.info("Timeout error")
                raise tornado.gen.TimeoutError("Timeout")
            self.logger.debug("Received: %r", r)
            self.buffer += r
            # offset = max(0, len(self.buffer) - self.MATCH_TAIL)
            # match = self.rx_mml_end.search(self.buffer, offset)
            # if match:
            #     self.logger.debug("End of the block")
            #     r = self.buffer[:match.start()]
            #     self.buffer = self.buffer[match.end()]
            raise tornado.gen.Return(r)

    def shutdown_session(self):
        if self.profile.shutdown_session:
            self.logger.debug("Shutdown session")
            self.profile.shutdown_session(self.script)


class DigestAuth(object):
    """
    Append HTTP Digest authorisation headers
    """

    name = "digestauth"

    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password
        self.last_nonce = None
        self.last_realm = None
        self.last_opaque = None
        self.request_id = 1

    def get_digest(self, uri, realm, method):
        """

        :param uri:
        :param realm:
        :param method: GET/POST
        :return:
        """
        # print("Get Digest", uri, realm, method, self.user, self.password)
        A1 = "%s:%s:%s" % (self.user, realm, self.password)
        A2 = "%s:%s" % (method, uri)

        HA1 = hashlib.md5(smart_bytes(A1)).hexdigest()
        HA2 = hashlib.md5(smart_bytes(A2)).hexdigest()

        return HA1, HA2

    def build_digest_header(self, url, method, digest_response):
        """

        :param url: query URL
        :param method: GET/POST method
        :param digest_response:  dict response header
        :type digest_response: dict
        :return:
        """
        # p_parsed = urlparse(url)
        # uri = p_parsed.path or "/"
        uri = url
        qop = digest_response.get("qop", "")
        realm = digest_response["realm"] if "realm" in digest_response else self.last_realm
        nonce = digest_response["nonce"] if "nonce" in digest_response else self.last_nonce
        algorithm = digest_response.get("algorithm")
        opaque = digest_response.get("opaque")

        HA1, HA2 = self.get_digest(uri, realm, method)

        if nonce == self.last_nonce:
            self.request_id += 1
        else:
            self.request_id = 1
        ncvalue = "%08x" % self.request_id

        s = nonce.encode("utf-8")
        # s += time.ctime().encode('utf-8')
        s += os.urandom(8)
        cnonce = hashlib.sha1(smart_bytes(s)).hexdigest()[:16]

        if not qop:
            respdig = hashlib.md5(smart_bytes("%s:%s:%s" % (HA1, nonce, HA2))).hexdigest()
        elif qop == "auth" or "auth" in qop.split(","):
            noncebit = "%s:%s:%s:%s:%s" % (nonce, ncvalue, cnonce, "auth", HA2)
            respdig = hashlib.md5(smart_bytes("%s:%s" % (HA1, noncebit))).hexdigest()
        else:
            respdig = None

        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' 'response="%s"' % (
            self.user,
            realm,
            nonce,
            uri,
            respdig,
        )

        if opaque:
            base += ', opaque="%s"' % opaque
        if algorithm:
            base += ', algorithm="%s"' % algorithm
        # if entdig:
        #     base += ', digest="%s"' % entdig
        if qop:
            base += ', qop="auth", nc=%s, cnonce="%s"' % ("%08x" % self.request_id, cnonce)
        self.last_nonce = nonce
        self.last_realm = realm
        self.last_opaque = opaque

        return "Digest %s" % (str(base))
