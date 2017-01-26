# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Healthcheck endpoint
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import tornado.web


class HealthRequestHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        self.write("OK")
