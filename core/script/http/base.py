# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import ujson
# NOC modules
from noc.core.log import PrefixLoggerAdapter
from noc.core.http.client import fetch_sync

from noc.config import config


class HTTP(object):
    CONNECT_TIMEOUT = config.http_client.connect_timeout
    REQUEST_TIMEOUT = config.http_client.request_timeout

    class HTTPError(Exception):
        pass

    def __init__(self, script):
        self.script = script
        self.logger = PrefixLoggerAdapter(script.logger, "http")

    def get_url(self, path):
        address = self.script.credentials["address"]
        port = self.script.credentials.get("http_port")
        if port:
            address += ":%s" % port
        proto = self.script.credentials.get("http_protocol", "http")
        return "%s://%s%s" % (proto, address, path)

    def get(self, path, headers=None, json=False, eof_mark=None):
        """
        Perform HTTP GET request
        :param path: URI
        :param headers: Dict of additional headers
        :param json: Decode json if set to True
        :param eof_mark: Waiting eof_mark in stream for end session (perhaps device return length 0)
        """
        self.logger.debug("GET %s", path)
        code, headers, result = fetch_sync(
            self.get_url(path),
            headers=headers,
            follow_redirects=True,
            validate_cert=False,
            eof_mark=eof_mark
        )
        if not (200 <= code <= 299):
            raise self.HTTPError("HTTP Error %d" % code)
        if json:
            try:
                result = ujson.loads(result)
            except ValueError as e:
                raise self.HTTPError("Failed to decode JSON: %s", e)
        self.logger.debug("Result: %r", result)
        return result

    def post(self, path, data, headers=None, json=False):
        """
        Perform HTTP GET request
        :param path: URI
        :param headers: Dict of additional headers
        :param json: Decode json if set to True
        """
        self.logger.debug("POST %s %s", path, data)
        code, headers, result = fetch_sync(
            self.get_url(path),
            method="POST",
            headers=headers,
            follow_redirects=True,
            validate_cert=False
        )
        if not (200 <= code <= 299):
            raise self.HTTPError("HTTP Error %d" % code)
        if json:
            try:
                return ujson.loads(result)
            except ValueError as e:
                raise self.HTTPError("Failed to decode JSON: %s", e)
        self.logger.debug("Result: %r", result)
        return result

    def close(self):
        pass
