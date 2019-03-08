# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# RTSP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.rtsp.client import fetch_sync
from noc.core.error import NOCError, ERR_HTTP_UNKNOWN
from noc.core.handler import get_handler
from noc.core.script.http.middleware.base import BaseMiddleware
from noc.core.script.http.middleware.loader import loader


class RTSP(object):
    class RTSPError(NOCError):
        default_code = ERR_HTTP_UNKNOWN

    def __init__(self, script):
        self.script = script
        if script:  # For testing purposes
            self.logger = PrefixLoggerAdapter(script.logger, "rtsp")
        self.headers = {}
        self.session_started = False
        self.request_id = 1
        self.session_id = None
        self.request_middleware = None
        if self.script:  # For testing purposes
            self.setup_middleware()

    def get_url(self, path, port=None):
        address = self.script.credentials["address"]
        if not port:
            port = self.script.credentials.get("http_port")
        if port:
            address += ":%s" % port
        return "rtsp://%s%s" % (address, path)

    def options(self, stream_path):
        """
        The OPTIONS method

        :param stream_path:
        :return:
        """
        return self.rtsp(stream_path)

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
        self.ensure_session()
        url = self.get_url(path, port=554)
        hdr = self._get_effective_headers(headers)
        if self.request_middleware:
            for mw in self.request_middleware:
                url, _, hdr = mw.process_get(url, "", hdr)
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

    def _get_effective_headers(self, headers):
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

    def ensure_session(self):
        if not self.session_started:
            self.session_started = True
            self.setup_session()

    def setup_session(self):
        if self.script.profile.setup_http_session:
            self.logger.debug("Setup rtsp session")
            self.script.profile.setup_http_session(self.script)

    def shutdown_session(self):
        if self.script.profile.shutdown_http_session:
            self.logger.debug("Shutdown rtsp session")
            self.script.profile.shutdown_http_session(self.script)

    def setup_middleware(self):
        mw_list = self.script.profile.get_http_request_middleware(self.script)
        if not mw_list:
            return
        self.request_middleware = []
        for mw_cfg in mw_list:
            if isinstance(mw_cfg, tuple):
                name, cfg = mw_cfg
            else:
                name, cfg = mw_cfg, {}
            if "." in name:
                # Handler
                mw_cls = get_handler(name)
                assert mw_cls
                assert isinstance(mw_cls, BaseMiddleware)
            else:
                # Middleware name
                mw_cls = loader.get_class(name)
            self.request_middleware += [mw_cls(self, **cfg)]
