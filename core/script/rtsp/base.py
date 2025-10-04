# ----------------------------------------------------------------------
# RTSP class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from urllib.request import parse_http_list, parse_keqv_list
import asyncio
from typing import Tuple, Dict, Any

# Third-party modules
import hashlib

# NOC modules
from noc.config import config
from noc.core.comp import smart_bytes, smart_text
from noc.core.span import Span
from noc.core.ioloop.util import IOLoopContext
from noc.core.perf import metrics
from ..cli.base import BaseCLI
from ..cli.stream import BaseStream
from .error import RTSPConnectionRefused, RTSPAuthFailed, RTSPBadResponse, RTSPError

DEFAULT_PROTOCOL = b"RTSP/1.0"
DEFAULT_USER_AGENT = smart_bytes(config.http_client.user_agent)
MULTIPLE_HEADER = {"WWW-Authenticate"}


class RTSPBase(BaseCLI):
    name = "rtsp"
    BUFFER_SIZE = config.activator.buffer_size
    MATCH_TAIL = 256
    SYNTAX_ERROR_CODE = b"+@@@NOC:SYNTAXERROR@@@+"

    def __init__(self, script, tos=None):
        super().__init__(script, tos)
        self.path = None
        self.cseq = 1
        self.method = None
        self.headers: Dict[str, Any] = None
        self.auth = None
        self.buffer: bytes = b""
        self.is_started = False
        self.result = None
        self.error = None
        self.close_timeout = None
        self.current_timeout = None
        self.rx_rtsp_end = "\r\n\r\n"

    def get_stream(self) -> BaseStream:
        return RTSPStream(self)

    def get_uri(self, port: int = None) -> str:
        address = self.script.credentials.get("address")
        if not port:
            port = RTSPStream.default_port
        if port:
            address += ":%s" % port
        return "rtsp://%s%s" % (address, self.path)

    async def send(self, method: str = None, body: str = None):
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
            smart_bytes(method),
            smart_bytes(self.get_uri()),
            DEFAULT_PROTOCOL,
            b"\r\n".join(b"%s: %s" % (smart_bytes(k), smart_bytes(h[k])) for k in h),
            smart_bytes(body),
        )
        self.logger.debug("Send: %r", req)
        await self.stream.write(req)
        self.cseq += 1

    async def submit(self):
        # Create iostream and connect, when necessary
        if not self.stream:
            try:
                await self.start_stream()
            except ConnectionRefusedError:
                self.error = RTSPConnectionRefused("Connection refused")
                return None
        # Perform all necessary login procedures
        if not self.is_started:
            self.is_started = True
            await self.send("OPTIONS")
            await self.get_rtsp_response()
            if self.error and self.error.code == 401:
                self.logger.info("Authentication needed")
                self.auth = DigestAuth(
                    user=self.script.credentials.get("user"),
                    password=self.script.credentials.get("password"),
                )
                # Send command
        await self.send()
        return await self.get_rtsp_response()

    async def get_rtsp_response(self):
        result = []
        header_sep = b"\r\n\r\n"
        while True:
            r = await self.read_until_end()
            # r = r.strip()
            # Process header
            if header_sep not in r:
                self.result = ""
                self.error = RTSPBadResponse("Missed header separator")
                return None
            header, r = r.split(header_sep, 1)
            code, headers, msg = self.parse_rtsp_header(header)
            self.headers = headers
            self.logger.debug(
                "Parsed received, err code: %d, err message: %s, headers: %s", code, msg, headers
            )
            if code == 401:
                self.result = ""
                self.error = RTSPAuthFailed("%s (code=%s)" % (msg, code), code=int(code))
                return None
            if not 200 <= code <= 299:
                # RTSP Error
                self.result = ""
                self.error = RTSPError("%s (code=%s)" % (msg, code), code=int(code))
                return None
            result += [r]
            break
        self.result = smart_text(b"".join(result))
        return self.result

    @staticmethod
    def parse_rtsp_header(data: bytes) -> Tuple[int, Dict[str, Any], bytes]:
        code, headers, msg = 200, {}, b""
        for line in data.splitlines():
            if line.startswith(b"RTSP/1.0"):
                _, code, msg = line.split(None, 2)
            elif b":" in line:
                h, v = line.split(b":", 1)
                h, v = smart_text(h), smart_text(v)
                if h in MULTIPLE_HEADER:
                    if h not in headers:
                        headers[h] = {}
                    auth, line = v.split(None, 1)
                    items = parse_http_list(line)
                    headers[h][auth] = parse_keqv_list(items)
                    continue
                headers[h] = v.strip()
        return int(code), headers, msg

    def execute(self, path, method, **kwargs):
        """
        Perform request and return result
        :param path:
        :param method:
        :param kwargs:
        :return:
        """
        self.buffer = b""
        self.path = path
        self.method = method
        self.error = None
        with Span(
            server=self.script.credentials.get("address"), service=self.name, in_label=self.method
        ) as s:
            with IOLoopContext() as loop:
                loop.run_until_complete(self.submit())
            if self.error:
                if s:
                    s.error_text = str(self.error)
                raise self.error
            return self.result

    async def read_until_end(self):
        while True:
            try:
                metrics["cli_reads", ("proto", self.name)] += 1
                r = await self.stream.read(self.BUFFER_SIZE)
                if r == self.SYNTAX_ERROR_CODE:
                    metrics["cli_syntax_errors", ("proto", self.name)] += 1
                    return self.SYNTAX_ERROR_CODE
                metrics["cli_read_bytes", ("proto", self.name)] += len(r)
                if self.script.to_track:
                    self.script.push_cli_tracking(r, self.state)
            except asyncio.TimeoutError:
                self.logger.info("Timeout error")
                metrics["cli_timeouts", ("proto", self.name)] += 1
                # IOStream must be closed to prevent hanging read callbacks
                self.close_stream()
                raise asyncio.TimeoutError("Timeout")  # @todo: Uncaught
            self.logger.debug("Received: %r", r)
            self.buffer += r
            return r

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

        base = 'username="%s", realm="%s", nonce="%s", uri="%s", response="%s"' % (
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


class RTSPStream(BaseStream):
    default_port = 554
