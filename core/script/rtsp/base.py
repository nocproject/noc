# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RTSP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import hashlib
import os
import urllib2
from urlparse import urlparse
# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.rtsp.client import fetch_sync
from noc.core.error import NOCError, ERR_RTSP_UNKNOWN


DEFAULT_RTSP_PORT = 554


class RTSP(object):
    class RTSPError(NOCError):
        default_code = ERR_RTSP_UNKNOWN

    def __init__(self, script):
        self.script = script
        if script:  # For testing purposes
            self.logger = PrefixLoggerAdapter(script.logger, "rtsp")
        self.headers = {}
        self.session_started = False
        self.request_id = 2
        self.session_id = None
        self.auth = None

    def get_url(self, path, port=None):
        address = self.script.credentials["address"]
        if not port:
            port = DEFAULT_RTSP_PORT
        if port:
            address += ":%s" % port
        return "rtsp://%s%s" % (address, path)

    def options(self, stream_path):
        """
        The OPTIONS method

        :param stream_path:
        :return:
        """
        return self.rtsp(stream_path, "OPTIONS")

    def describe(self, stream_path):
        """
        The DESCRIBE method retrieves the description of a presentation or
        media object identified by the request URL from a server

        :param stream_path:
        :return:
        """
        return self.rtsp(stream_path, "DESCRIBE")

    def play(self):
        """
        The PLAY method tells the server to start sending data via the
        mechanism specified in SETUP.
        :return:
        """
        raise NotImplementedError()

    def pause(self):
        """
        The PAUSE request causes the stream delivery to be interrupted
        (halted) temporarily. If the request URL names a stream, only
        playback and recording of that stream is halted.
        :return:
        """
        raise NotImplementedError()

    def setup(self):
        """
        The SETUP request for a URI specifies the transport mechanism to be
        used for the streamed media. A client can issue a SETUP request for a
        stream that is already playing to change transport parameters, which
        a server MAY allow.
        :return:
        """
        raise NotImplementedError()

    def teardown(self):
        """
        The TEARDOWN request stops the stream delivery for the given URI,
        freeing the resources associated with it.
        :return:
        """
        raise NotImplementedError()

    def rtsp(self, path, method=None, headers=None):
        if not method:
            method = "OPTIONS *"
        url = self.get_url(path, port=554)
        self.ensure_session(url)
        hdr = self._get_effective_headers(url, headers, method)
        code, headers, result = fetch_sync(
            url,
            headers=hdr,
            request_timeout=60,
            follow_redirects=True,
            validate_cert=False,
            method=method,
        )
        if not 200 <= code <= 299:
            raise self.RTSPError(msg="RTSP Error (%s)" % result[:256], code=code)
        return result

    def close(self):
        if self.session_started:
            self.shutdown_session()

    def _get_effective_headers(self, url, headers, method):
        """
        Append session headers when necessary. Apply effective cookies
        :param headers:
        :return:
        """
        if self.headers:
            if headers:
                headers = headers.copy()
            else:
                headers = {}
            headers.update(self.headers)
        elif not headers:
            headers = {}
        headers["CSeq"] = self.request_id
        self.request_id += 1
        if self.auth:
            headers["Authorization"] = self.auth.build_digest_header(url, method, headers)
            # headers.update(self.auth("", method, headers))
        return headers

    def set_header(self, name, value):
        """
        Set HTTP header to be set with all following requests
        :param name:
        :param value:
        :return:
        """
        self.logger.debug("Set header: %s = %s", name, value)
        self.headers[name] = str(value)

    def set_session_id(self, session_id):
        """
        Set session_id to be reused by middleware
        :param session_id:
        :return: None
        """
        if session_id is not None:
            self.session_id = session_id
        else:
            self.session_id = None

    def ensure_session(self, url):
        if not self.session_started:
            self.session_started = True
            self.setup_session(url=url)

    def setup_session(self, url):
        self.logger.debug("Setup rtsp session")
        code, headers, result = fetch_sync(
            url,
            headers={"CSeq": self.request_id},
            request_timeout=60,
            follow_redirects=True,
            validate_cert=False,
            method="OPTIONS",
        )
        self.request_id += 1
        if code == 401 and not self.auth:
            # Unauthorized
            if "WWW-Authenticate" in headers and headers["WWW-Authenticate"][0].startswith("Digest"):
                items = urllib2.parse_http_list(headers["WWW-Authenticate"][0][7:])
                digest_response = urllib2.parse_keqv_list(items)
                self.auth = DigestAuth(user=self.script.credentials.get("user"),
                                       password=self.script.credentials.get("password"))
                headers["Authorization"] = self.auth.build_digest_header(url, "OPTIONS", digest_response)
        elif not 200 <= code <= 299:
            raise self.RTSPError(msg="RTSP Error (%s)" % result[:256], code=code)

    def shutdown_session(self):
        if self.script.profile.shutdown_http_session:
            self.logger.debug("Shutdown rtsp session")


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
        A1 = '%s:%s:%s' % (self.user, realm, self.password)
        A2 = '%s:%s' % (method, uri)

        HA1 = hashlib.md5(A1).hexdigest()
        HA2 = hashlib.md5(A2).hexdigest()

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
        algorithm = digest_response.get('algorithm')
        opaque = digest_response.get('opaque')

        HA1, HA2 = self.get_digest(uri, realm, method)

        if nonce == self.last_nonce:
            self.request_id += 1
        else:
            self.request_id = 1
        ncvalue = '%08x' % self.request_id

        s = nonce.encode('utf-8')
        # s += time.ctime().encode('utf-8')
        s += os.urandom(8)
        cnonce = (hashlib.sha1(s).hexdigest()[:16])

        if not qop:
            respdig = hashlib.md5("%s:%s:%s" % (HA1, nonce, HA2)).hexdigest()
        elif qop == 'auth' or 'auth' in qop.split(','):
            noncebit = "%s:%s:%s:%s:%s" % (
                nonce, ncvalue, cnonce, 'auth', HA2
            )
            respdig = hashlib.md5("%s:%s" % (HA1, noncebit)).hexdigest()
        else:
            respdig = None

        base = 'username="%s", realm="%s", nonce="%s", uri="%s", ' \
               'response="%s"' % (self.user, realm, nonce, uri, respdig)

        if opaque:
            base += ', opaque="%s"' % opaque
        if algorithm:
            base += ', algorithm="%s"' % algorithm
        # if entdig:
        #     base += ', digest="%s"' % entdig
        if qop:
            base += ', qop="auth", nc=%s, cnonce="%s"' % (
                '%08x' % self.request_id, cnonce)
        self.last_nonce = nonce
        self.last_realm = realm
        self.last_opaque = opaque

        return 'Digest %s' % (str(base))
