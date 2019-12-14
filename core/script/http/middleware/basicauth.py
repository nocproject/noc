# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP Basic Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import codecs

# NOC modules
from .base import BaseMiddleware
from noc.core.comp import smart_text


class BasicAuthMiddeware(BaseMiddleware):
    """
    Append HTTP Basic authorisation headers
    """

    name = "basicauth"

    def __init__(self, http, user=None, password=None):
        super(BasicAuthMiddeware, self).__init__(http)
        self.user = user
        self.password = password

    def process_request(self, url, body, headers):
        user = self.user or self.http.script.credentials.get("user")
        password = self.password or self.http.script.credentials.get("password")
        if user and password:
            uh = smart_text("%s:%s" % (user, password))
            headers["Authorization"] = (
                b"Basic %s" % codecs.encode(uh.encode("utf-8"), "base64").strip()
            )
        return url, body, headers
