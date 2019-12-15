# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Authentication handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import codecs

# Third-party modules
import tornado.web
from noc.config import config
from noc.core.comp import smart_bytes


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

        def api_success(access, key_name=None):
            self.set_status(200, "OK")
            self.set_header("X-NOC-API-Access", access)
            if key_name:
                self.set_header("Remote-User", key_name)

        def fail(user_name=None, reason=None):
            self.set_status(401, "Not authorized")
            self.service.logger.error(
                "[%s|%s] Denied: %s",
                user_name or "NOT SET",
                self.request.remote_ip,
                reason or "Unspecified reason",
            )

        user = self.get_secure_cookie(self.USER_COOKIE)
        if user:
            return success(user)
        elif self.request.headers.get("Private-Token"):
            name, access = self.service.get_api_access(
                self.request.headers.get("Private-Token"), self.request.remote_ip
            )
            if not name:
                return fail(reason="API Key not found")
            if not access:
                return fail(user_name=name, reason="API Key has not access")
            return api_success(access, name)
        elif self.request.headers.get("Authorization"):
            # Fallback to the basic auth
            ah = self.request.headers.get("Authorization")
            if ah.startswith("Basic "):
                c = codecs.decode(smart_bytes(ah[6:]), "base64")
                if ":":
                    user, password = c.split(":", 1)
                    credentials = {"user": user, "password": password, "ip": self.request.remote_ip}
                    if self.service.authenticate(self, credentials):
                        return success(user)
                    else:
                        return fail(user_name=user, reason="Authentication failed")
        return fail()
