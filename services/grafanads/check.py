# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# check handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import tornado.web


class CheckHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("OK")
