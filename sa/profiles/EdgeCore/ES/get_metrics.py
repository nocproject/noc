# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# EdgeCore.ES.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "EdgeCore.ES.get_metrics"

    ALL_IFACE_METRICS = set(["Interface | Errors | CRC", "Interface | Errors | Frame"])

    def collect_profile_metrics(self, metrics):
        if self.has_capability("DB | Interfaces"):
            self.logger.debug("Merics %s" % metrics)
            if self.ALL_IFACE_METRICS.intersection(set(m.metric for m in metrics)):
                # check
                self.collect_iface_metrics(metrics)

    def collect_iface_metrics(self, metrics):
        # if not (self.ALL_SLA_METRICS & set(metrics)):
        #    return  # NO SLA metrics requested
        ts = self.get_ts()
        m = self.get_iface_metrics()
        print m
        for bv in metrics:
            if bv.metric in self.ALL_IFACE_METRICS:
                id = tuple(bv.path + [bv.metric])
                if id in m:
                    print(id)
                    self.set_metric(
                        id=bv.id,
                        metric=bv.metric,
                        value=m[id],
                        ts=ts,
                        path=bv.path,
                    )

    def get_iface_metrics(self):
        r = {}
        v = self.cli("show interfaces counters")
        v = self.profile.parse_ifaces(v)
        metric_map = {"CRC Align Errors": "Interface | Errors | CRC",
                      "Frames Too Long": "Interface | Errors | Frame"}
        print v
        for iface in v:
            print iface
            for m in metric_map:
                if m not in v[iface]:
                    continue
                r[("", "", "", self.profile.convert_interface_name(iface), metric_map[m])] = int(v[iface][m])
        return r
