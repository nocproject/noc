# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Healthcheck endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.web


class HealthRequestHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        service = self.get_argument("service", None)
        if service and not self.service.is_valid_health_check(service):
            raise tornado.web.HTTPError(400, "Invalid service id")
        status, message = self.service.get_health_status()
        self.set_status(status, message)
