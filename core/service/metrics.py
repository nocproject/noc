# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prometeus metrics endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import string
# Third-party modules
import tornado.web

TR = string.maketrans(".-\"", "___")


class MetricsHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        def q(s):
            return s.translate(TR)

        labels = [
            "service=\"%s\"" % self.service.name
        ]
        if self.service.pooled:
            labels += ["pool=\"%s\"" % self.service.config.pool]
        labels = ",".join(labels)
        out = []
        mdata = self.service.get_mon_data()
        for m in mdata:
            qm = q(m)
            out += ["# TYPE %s gauge" % qm]
            out += ["%s{%s} %s" % (qm, labels, mdata[m])]
        self.add_header("Content-Type", "text/plain; version=0.0.4")
        self.write("\n".join(out))
