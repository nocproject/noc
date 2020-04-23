# ----------------------------------------------------------------------
# Prometeus metrics endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import string

# Third-party modules
import tornado.web
from noc.config import config

if hasattr(string, "maketrans"):
    TR = string.maketrans('.-"', "___")
else:
    TR = str.maketrans('.-"', "___")


class MetricsHandler(tornado.web.RequestHandler):
    """
    Prometheus compatible metrics endpoint
    """

    def initialize(self, service):
        self.service = service

    def get(self):
        """
        :return: list
        """
        labels = {"service": self.service.name, "node": config.node}
        if self.service.pooled:
            labels["pool"] = config.pool
        if hasattr(self.service, "slot_number"):
            labels["slot"] = self.service.slot_number
        out = []
        mdata = self.service.get_mon_data()
        for key in mdata:
            if key == "pid":
                continue
            metric_name = key
            local_labels = {}
            if isinstance(mdata[key], (bool, str)):
                continue
            if isinstance(key, tuple):
                metric_name = key[0]
                for k in key[1:]:
                    local_labels.update({k[0]: k[1]})
            local_labels.update(labels)
            cleared_name = str(metric_name).translate(TR).lower()
            value = mdata[key]
            if value is None:
                continue
            if hasattr(value, "iter_prom_metrics"):
                out += list(value.iter_prom_metrics(cleared_name, local_labels))
            else:
                out_labels = ",".join(
                    ['%s="%s"' % (i.lower(), local_labels[i]) for i in local_labels]
                )
                out += ["# TYPE %s untyped" % cleared_name]
                out += ["%s{%s} %s" % (cleared_name, out_labels, value)]
        self.add_header("Content-Type", "text/plain; version=0.0.4")
        self.write("\n".join(out) + "\n")
