# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP Digest Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import hashlib
import os

# Third-party modules
from six.moves.urllib.parse import urlparse
from six.moves.urllib.request import parse_http_list, parse_keqv_list

# NOC modules
from .base import BaseMiddleware
from noc.core.http.client import fetch_sync
from noc.core.comp import smart_bytes


class DigestAuthMiddeware(BaseMiddleware):
    """
    Append HTTP Digest authorisation headers
    """

    name = "digestauth"

    def __init__(self, http):
        super(DigestAuthMiddeware, self).__init__(http)
        self.user = self.http.script.credentials.get("user")
        self.password = self.http.script.credentials.get("password")
        self.method = "GET"
        self.last_nonce = None
        self.last_realm = None
        self.last_opaque = None
        self.request_id = 1

    def get_digest(self, uri, realm):
        """

        :param uri:
        :param realm:
        :param method: GET/POST
        :return:
        """
        A1 = "%s:%s:%s" % (self.user, realm, self.password)
        A2 = "%s:%s" % (self.method, uri)

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

    def process_request(self, url, body, headers):
        if not headers:
            headers = {}
        # First query - 401
        code, resp_headers, result = fetch_sync(
            url,
            headers=None,
            request_timeout=60,
            follow_redirects=True,
            allow_proxy=False,
            validate_cert=False,
        )
        if "WWW-Authenticate" in resp_headers and resp_headers["WWW-Authenticate"].startswith(
            "Digest"
        ):
            items = parse_http_list(resp_headers["WWW-Authenticate"][7:])
            digest_response = parse_keqv_list(items)
            headers["Authorization"] = self.build_digest_header(url, self.method, digest_response)
        return url, body, headers
