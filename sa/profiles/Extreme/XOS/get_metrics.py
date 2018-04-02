# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Extreme.XOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import division
from itertools import groupby
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript


class Script(GetMetricsScript):
    name = "Extreme.XOS.get_metrics"

    ALL_METRICS = {"Interface | DOM | Temperature": "collect_dom_metrics",
                   "Interface | DOM | Voltage": "collect_dom_metrics",
                   "Interface | DOM | RxPower": "collect_dom_metrics",
                   "Interface | DOM | Bias Current": "collect_dom_metrics",
                   "Interface | DOM | TxPower": "collect_dom_metrics",
                   "CPU | Usage": "",
                   "Memory | Usage": ""}
    TYPE = {
        "Check | Avail": "gauge",
        "Radio | TxPower": "gauge",
        "Radio | Quality": "gauge",
        "Interface | Load | In": "counter",
        "Interface | Load | Out": "counter",
        "Radio | Channel | Util": "gauge",
        "Radio | Channel | Free": "gauge",
        "Radio | Channel | Busy": "gauge",
        "Radio | Channel | TxFrame": "gauge",
        "Radio | Channel | RxFrame": "gauge",
        "Interface | Packets | In": "counter",
        "Interface | Packets | Out": "counter",
        "Interface | Errors | In": "counter",
        "Interface | Errors | Out": "counter"
    }

    @classmethod
    def get_metric_type(cls, name):
        return cls.TYPE.get(name, "gauge")

    def collect_profile_metrics(self, metrics):
        self.logger.debug("Merics %s" % metrics)
        collected_metrics = set(self.ALL_METRICS).intersection(set(m.metric for m in metrics))
        if collected_metrics:
            self.collect_cli_metrics(metrics)

    def collect_cli_metrics(self, metrics):
        procc = []
        m = {}
        paths = {}
        ts = self.get_ts()
        # m = self.get_cli_metrics()
        # Getting metrics
        for bv in metrics:
            if bv.metric not in self.ALL_METRICS:
                continue
            if self.ALL_METRICS[bv.metric] not in procc:
                m_handler = getattr(self, self.ALL_METRICS[bv.metric], None)
                if m_handler:
                    m.update(m_handler())
                    for k, v in groupby(sorted(m, key=lambda x: x[-1]), key=lambda x: x[-1]):
                        paths[k] = list(v)
            # @todo Refactoring
            if bv.path:
                if tuple(bv.path + [bv.metric]) not in m:
                    continue
                pp = [tuple(bv.path + [bv.metric])]
            elif "slot" in m:
                pp = paths[bv.metric]
            else:
                continue
            for p in pp:
                self.set_metric(
                    id=bv.id,
                    metric=bv.metric,
                    value=m[p],
                    type=self.get_metric_type(bv.metric),
                    ts=ts,
                    path=p[:-1],
                )
            # if bv.path:
            #     id = tuple(bv.path + [bv.metric])
            # else:
            #     id = m[slot]
            # if id in m:
            #     self.set_metric(
            #         id=bv.id,
            #         metric=bv.metric,
            #         value=m[id],
            #         type=self.get_metric_type(bv.metric),
            #         ts=ts,
            #         path=bv.path,
            #     )

    def collect_dom_metrics(self):
        r = {}
        for m in self.scripts.get_dom_status():
            iface = m["interface"]
            if m["temp_c"] is not None:
                r[("", "", "", iface, "Interface | DOM | Temperature")] = m["temp_c"]
            if m["voltage_v"] is not None:
                r[("", "", "", iface, "Interface | DOM | Voltage")] = m["voltage_v"]
            if m["optical_rx_dbm"] is not None:
                r[("", "", "", iface, "Interface | DOM | RxPower")] = m["optical_rx_dbm"]
            if m["current_ma"] is not None:
                r[("", "", "", iface, "Interface | DOM | Bias Current")] = m["current_ma"]
            if m["optical_tx_dbm"] is not None:
                r[("", "", "", iface, "Interface | DOM | TxPower")] = m["optical_tx_dbm"]
        return r
