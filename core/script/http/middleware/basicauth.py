# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# HTTP Basic Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseMiddleware


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
            headers["Authorization"] = "Basic %s" % (
                "%s:%s" % (user, password)
            ).encode("base64").strip()
        return url, body, headers
