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
        labels = [
            "service=\"%s\"" % self.service.name,
            "node=\"%s\"" % config.node,
        ]
        if self.service.pooled:
            labels += ["pool=\"%s\"" % config.pool]
        if self.service.name in ("discovery", "ping"):
            labels += ["slot=\"%s\"" % self.service.slot_number]
        labels = ",".join(labels)
        out = []
        mdata = self.service.get_mon_data()
        for key in mdata:
            if isinstance(mdata[key], six.string_types) or isinstance(mdata[key], bool):
                continue
            qm = str(key).translate(TR)
            out += ["# TYPE %s untyped" % qm.lower()]
            out += ["%s{%s} %s" % (qm.lower(), labels.lower(), mdata[key])]
        self.add_header("Content-Type", "text/plain; version=0.0.4")
        self.write("\n".join(out)+"\n")
