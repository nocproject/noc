# ---------------------------------------------------------------------
# Authentication handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.web
import ujson

# NOC modules
from .auth import AuthRequestHandler


class IsLoggedRequestHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        """
        Check secure cookie
        """
        user = self.get_secure_cookie(AuthRequestHandler.USER_COOKIE)
        self.set_status(200, "OK")
        if user:
            self.write(ujson.dumps(True))
            return
        self.write(ujson.dumps(False))
