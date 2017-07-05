# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prometeus metrics endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import tornado.web


class MetricsHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        out = []
        mdata = self.service.get_mon_data()
        for m in mdata:
            out += ["# TYPE %s gauge" % m]
            out += ["%s %s" % (m, mdata[m])]
        self.add_header("Content-Type", "text/plain; version=0.0.4")
        self.write("\n".join(out))
