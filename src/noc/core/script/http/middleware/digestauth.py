# ----------------------------------------------------------------------
# HTTP Digest Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import hashlib
import os
from urllib.parse import urlparse
from urllib.request import parse_http_list, parse_keqv_list

# NOC modules
from .base import BaseMiddleware
from noc.core.http.sync import HttpClient
from noc.core.comp import smart_bytes


class DigestAuthMiddeware(BaseMiddleware):
    """Append HTTP Digest authorisation headers"""

    name = "digestauth"

    def __init__(self, http, eof_mark=None) -> None:
        super().__init__(http)
        self.logger = http.logger
        self.eof_mark = eof_mark
        self.user = self.http.script.credentials.get("user")
        self.password = self.http.script.credentials.get("password")
        self.method = "GET"
        self.last_nonce = None
        self.last_realm = None
        self.last_opaque = None
        self.request_id = 1

    def get_digest(self, uri, realm):
        """Calculate credential Digest

        Args:
            uri
            realm
        """
        A1 = f"{self.user}:{realm}:{self.password}".encode()
        A2 = f"{self.method}:{uri}".encode()

        HA1 = hashlib.md5(A1).hexdigest()
        HA2 = hashlib.md5(A2).hexdigest()

        return HA1, HA2

    def build_digest_header(self, url, method, digest_response):
        """
        Args:
            url: query URL
            method: GET/POST method
            digest_response (dict): dict response header
        """
        self.logger.debug(
            "[%s] Build digest for %s, on response %s", self.name, url, digest_response
        )
        p_parsed = urlparse(url)
        uri = p_parsed.path or "/"
        qop = digest_response["qop"]
        realm = digest_response["realm"]
        nonce = digest_response["nonce"]
        algorithm = digest_response.get("algorithm")
        opaque = digest_response.get("opaque")

        HA1, HA2 = self.get_digest(uri, realm)

        if nonce == self.last_nonce:
            self.request_id += 1
        else:
            self.request_id = 1
        ncvalue = f"{self.request_id:08x}"

        s = nonce.encode("utf-8")
        # s += time.ctime().encode('utf-8')
        s += os.urandom(8)
        cnonce = hashlib.sha1(s).hexdigest()[:16]

        if not qop:
            respdig = hashlib.md5(smart_bytes(f"{HA1}:{nonce}:{HA2}")).hexdigest()
        elif qop == "auth" or "auth" in qop.split(","):
            noncebit = f"{nonce}:{ncvalue}:{cnonce}:{'auth'}:{HA2}"
            respdig = hashlib.md5(smart_bytes(f"{HA1}:{noncebit}")).hexdigest()
        else:
            respdig = None

        base = f'username="{self.user}", realm="{realm}", nonce="{nonce}", uri="{uri}", response="{respdig}"'

        if opaque:
            base += f', opaque="{opaque}"'
        if algorithm:
            base += f', algorithm="{algorithm}"'
        # if entdig:
        #     base += ', digest="%s"' % entdig
        if qop:
            base += f', qop="auth", nc={f"{self.request_id:08x}"}, cnonce="{cnonce}"'
        self.last_nonce = nonce
        self.last_realm = realm
        self.last_opaque = opaque
        return f"Digest {base!s}"

    def process_request(self, url, body, headers):
        if not headers:
            headers = {}
        self.logger.debug("[%s] Process middleware on: %s", self.name, url)
        # First query - 401
        with HttpClient(
            timeout=60,
            allow_proxy=False,
            validate_cert=False,
        ) as client:
            code, resp_headers, _result = client.get(url)
            self.logger.debug(
                "[%s] Response code %s, headers %s on: %s, body: %s",
                self.name,
                code,
                resp_headers,
                url,
                body,
            )
            if "WWW-Authenticate" in resp_headers and resp_headers["WWW-Authenticate"].startswith(
                b"Digest"
            ):
                items = parse_http_list(resp_headers["WWW-Authenticate"].decode()[7:])
                digest_response = parse_keqv_list(items)
                headers["Authorization"] = self.build_digest_header(
                    url, self.method, digest_response
                ).encode()
            self.logger.debug("[%s] Set headers, %s", self.name, headers)
            return url, body, headers
