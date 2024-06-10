# ----------------------------------------------------------------------
# HTTP Basic Auth Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import codecs

# NOC modules
from .base import BaseMiddleware


class BasicAuthMiddeware(BaseMiddleware):
    """
    Append HTTP Basic authorisation headers
    """

    name = "basicauth"

    def __init__(self, http, user=None, password=None):
        super().__init__(http)
        self.user = user
        self.password = password

    def process_request(self, url, body, headers):
        user = self.user or self.http.script.credentials.get("user")
        password = self.password or self.http.script.credentials.get("password")
        if user and password:
            uh = f"{user}:{password}".encode("utf-8")
            headers["Authorization"] = b"Basic %s" % codecs.encode(uh, "base64").strip()
        return url, body, headers
