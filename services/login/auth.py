# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Authentication handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import base64

# Third-party modules
import tornado.web
from noc.config import config


class AuthRequestHandler(tornado.web.RequestHandler):
    USER_COOKIE = "noc_user"
    USER_COOKIE_TTL = config.login.user_cookie_ttl  # % fixme probably unused

    def initialize(self, service):
        self.service = service

    def get(self, *args, **kwargs):
        """
        Checks Basic auth or noc_user secure cookie
        """

        def success(user):
            self.set_status(200, "OK")
            self.set_header("Remote-User", user)

        def fail():
            self.set_status(401, "Not authorized")

        user = self.get_secure_cookie(self.USER_COOKIE)
        if user:
            return success(user)
        elif self.request.headers.get("Authorization"):
            # Fallback to the basic auth
            ah = self.request.headers.get("Authorization")
            if ah.startswith("Basic "):
                c = base64.decodestring(ah[6:])
                if ":":
                    user, password = c.split(":", 1)
                    credentials = {
                        "user": user,
                        "password": password,
                        "ip": self.request.remote_ip
                    }
                    if self.service.authenticate(self, credentials):
                        return success(user)
        return fail()
