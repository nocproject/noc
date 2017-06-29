# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP methods implementation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import cStringIO
# Third-party modules
import pycurl
import ujson
# NOC modules
from noc.core.log import PrefixLoggerAdapter


class HTTP(object):
    CONNECT_TIMEOUT = 10
    REQUEST_TIMEOUT = 300

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

    def get_curl(self, path, headers=None):
        """
        Create and prepare Curl instance
        """
        # Build full URL
        url = self.get_url(path)
        # Prepare client
        is_ssl = self.script.credentials.get("http_protocol", "http") == "https"
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        if headers:
            c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.NOPROXY, "*")
        c.setopt(c.TIMEOUT, self.REQUEST_TIMEOUT)
        c.setopt(c.CONNECTTIMEOUT, self.CONNECT_TIMEOUT)
        c.setopt(c.FOLLOWLOCATION, 1)
        if is_ssl:
            c.setopt(c.SSL_VERIFYPEER, 0)
        return c

    def get(self, path, headers=None, json=False):
        """
        Perform HTTP GET request
        :param path: URI
        :param headers: Dict of additional headers
        :param json: Decode json if set to True
        """
        self.logger.debug("GET %s", path)
        buff = cStringIO.StringIO()
        c = self.get_curl(path, headers=headers)
        c.setopt(c.WRITEDATA, buff)
        try:
            c.perform()
        except pycurl.error as e:
            self.logger.error("HTTP Error: %s", e)
            raise self.HTTPError(str(e))
        result = buff.getvalue()
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
        buff = cStringIO.StringIO()
        c = self.get_curl(path, headers=headers)
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, data)
        c.setopt(c.WRITEDATA, buff)
        try:
            c.perform()
        except pycurl.error as e:
            self.logger.error("HTTP Error: %s", e)
            raise self.HTTPError(str(e))
        result = buff.getvalue()
        if json:
            try:
                return ujson.loads(result)
            except ValueError as e:
                raise self.HTTPError("Failed to decode JSON: %s", e)
        self.logger.debug("Result: %r", result)
        return result

    def close(self):
        pass
