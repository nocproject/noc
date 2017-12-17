# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "Alstec.24xx.get_metrics"

    ALL_IFACE_METRICS = set(["Interface | Errors | CRC", "Interface | Errors | Frame"])
    ALL_ENV_METRICS = set(["Environment | Electric current", "Environment | Sensor Status",
                           "Environment | Temperature", "Environment | Voltage"])

    def collect_profile_metrics(self, metrics):
        if self.has_capability("DB | Interfaces"):
            self.logger.debug("Merics %s" % metrics)
            if self.ALL_IFACE_METRICS.intersection(set(m.metric for m in metrics)) or \
                    self.ALL_ENV_METRICS.intersection(set(m.metric for m in metrics)):
                # check
                self.collect_iface_metrics(metrics)

    def collect_iface_metrics(self, metrics):
        # if not (self.ALL_SLA_METRICS & set(metrics)):
        #    return  # NO SLA metrics requested
        ts = self.get_ts()
        m = self.get_boxshso_metrics()
        self.logger.debug("Metrics: %s", m)
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
            elif bv.metric in self.ALL_ENV_METRICS:
                for path, value in six.iteritems(m):
                    if path[-1] == bv.metric:
                        self.set_metric(
                            id=bv.id,
                            metric=bv.metric,
                            value=value,
                            ts=ts,
                            path=path,
                        )

    def get_boxshso_metrics(self):
        modules = {"black_box": "show box-shso bb",
                   "battery_pack": "show box-shso bp",
                   "main_power_supply": "show box-shso pum"}
        r = {}
        for module, command in six.iteritems(modules):
            v = self.cli(command)
            v = self.profile.parse_kv_out(v)
            for m, v in six.iteritems(v):
                m = m.lower()
                metric = None
                if "temperature" in m:
                    metric = "Environment | Temperature"
                    v = float(v.split()[0])
                elif "voltage" in m:
                    metric = "Environment | Voltage"
                    v = float(v.split()[0])
                elif "current" in m:
                    metric = "Environment | Electric current"
                    v = float(v.split()[0]) * 1000.0
                elif "door state" in m:
                    metric = "Environment | Sensor Status"
                    v = bool("Open" in v)
                if not metric:
                    continue
                r[("", "", module, m, metric)] = v

        v = self.cli("show box-shso counters")
        v = self.profile.parse_kv_out(v)
        metric_map = {"CRC errors": "Interface | Errors | CRC",
                      "Invalid frame length": "Interface | Errors | Frame"}
        for iface in v:
            for m in metric_map:
                if m not in v[iface]:
                    continue
                r[("", "", "", "0/0", metric_map[m])] = int(v[iface][m])
        return r
