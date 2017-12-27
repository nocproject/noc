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
    """
    Prometheus compatible metrics
    """

    def initialize(self, service):
        self.service = service

    def get(self):
        """
        :return: list
        """
        labels = {
            "service": self.service.name,
            "node": config.node,
        }
        if self.service.pooled:
            labels.update({"pool": config.pool})
        if hasattr(self.service, "slot_number"):
            labels.update({"slot": self.service.slot_number})
        out = []
        mdata = self.service.get_mon_data()
        for key in mdata:
            metric_name = key
            local_labels = {}
            if isinstance(mdata[key], (bool, six.string_types)):
                continue
            if isinstance(key, tuple):
                metric_name = key[0]
                for k in key[1:]:
                    local_labels.update({k[0]: k[1]})
            local_labels.update(labels)
            out_labels = ",".join(["%s=%s" % (i.lower(), local_labels[i]) for i in local_labels])
            cleared_name = str(metric_name).translate(TR)
            out += ["# TYPE %s untyped" % cleared_name.lower()]
            out += ["%s{%s} %s" % (cleared_name.lower(), out_labels, mdata[key])]
        self.add_header("Content-Type", "text/plain; version=0.0.4")
        self.write("\n".join(out) + "\n")
