# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Monitoring endpoint
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import tornado.web


class MonRequestHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        self.write(
            self.service.get_mon_data()
        )
