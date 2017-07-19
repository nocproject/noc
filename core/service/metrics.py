# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prometeus metrics endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import string
import six
# Third-party modules
import tornado.web
from noc.config import config

TR = string.maketrans(".-\"", "___")


class MetricsHandler(tornado.web.RequestHandler):
    def initialize(self, service):
        self.service = service

    def get(self):
        def q(s):
            return s.translate(TR)

        labels = [
            "service=\"%s\"" % self.service.name,
            "node=\"%s\"" % config.node
        ]
        if self.service.pooled:
            labels += ["pool=\"%s\"" % config.pool]
        labels = ",".join(labels)
        out = []
        mdata = self.service.get_mon_data()
        for key in mdata:
            if isinstance(mdata[key], six.string_types) or isinstance(mdata[key], bool):
                continue
            qm = q(key)
            out += ["# TYPE %s counter" % qm]
            out += ["%s{%s} %s" % (qm, labels, mdata[key])]
        self.add_header("Content-Type", "text/plain; version=0.0.4")
        self.write("\n".join(out))
