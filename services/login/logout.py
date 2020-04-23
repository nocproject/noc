# ---------------------------------------------------------------------
# Authentication handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.web

# NOC modules
from .auth import AuthRequestHandler


class LogoutRequestHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        """
        Reset secure cookie
        """
        self.clear_cookie(AuthRequestHandler.USER_COOKIE)
        self.redirect("/", permanent=False)
