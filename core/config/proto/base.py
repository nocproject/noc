# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base config protocol class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from six.moves.urllib.parse import unquote, urlparse


class BaseProtocol(object):
    def __init__(self, config, url):
        self.config = config
        self.url = url
        # Parse url
        self.parsed_url = None
        self.url_query = {}
        self.parse_url(url)

    def load(self):
        raise NotImplementedError()

    def dump(self):
        raise NotImplementedError()

    def parse_url(self, url):
        self.parsed_url = urlparse(url)
        for q in self.parsed_url.query.split("&"):
            if not q or "=" not in q:
                continue
            k, v = q.split("=", 1)
            v = unquote(v)
            self.url_query[k] = v
