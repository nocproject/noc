# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Monitoring endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.web
import ujson


class MonRequestHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        self.write(ujson.dumps(self.service.get_mon_data()))
