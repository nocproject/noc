# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Authentication handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import tornado.web


class AuthRequestHandler(tornado.web.RequestHandler):
    USER_COOKIE = "noc_user"
    USER_COOKIE_TTL = 1  # 1 day

    def get(self, *args, **kwargs):
        """
        Checks Basic auth or noc_user secure cookie
        """
        original_uri = self.request.headers["X-Original-Uri"]
        user_cookie = self.get_secure_cookie(
            self.USER_COOKIE
        )
        if user_cookie:
            self.set_status(200, "OK")
        else:
            self.set_status(401, "Not authorized")
