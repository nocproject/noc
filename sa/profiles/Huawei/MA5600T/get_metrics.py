# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.lib.text import parse_kv


class Script(GetMetricsScript):
    name = "Huawei.MA5600T.get_metrics"

    kv_map = {"rx optical power(dbm)": "optical_rx_dbm",
              "tx optical power(dbm)": "optical_tx_dbm",
              "laser bias current(ma)": "current_ma",
              "temperature(c)": "temp_c",
              "voltage(v)": "voltage_v",
              "olt rx ont optical power(dbm)": "optical_rx_dbm_cpe"}

    @metrics(
        ["Interface | DOM | RxPower", "Interface | DOM | TxPower",
         "Interface | DOM | Voltage", "Interface | DOM | Bias Current"
         "Interface | DOM | Temperature"],
        # has_capability="Network | PON | OLT",
        access="C",  # CLI version
        volatile=False
    )
    def collect_dom_metrics(self, metrics):
        super(Script, self).collect_dom_metrics(metrics)
        self.collect_cpe_metrics(metrics)

    def collect_cpe_metrics(self, metrics):
        onts = self.scripts.get_cpe_status()  # Getting ONT List
        self.cli("config")
        self.cli("interface gpon 0/0")  # Fix from cpes
        for cc in onts:
            if cc.get("status", "") != "active":
                continue
            frame, slot, port, cpe_id = cc["id"].split("/")
            ipath = [cc["global_id"], "", "", "0"]
            mpath = ["", "", "", "/".join([frame, slot, port])]
            v = self.cli("display ont optical-info %s %s" % (port, cpe_id))
            m = parse_kv(self.kv_map, v)

            self.logger.debug("Collect %s, %s, %s", m, ipath, mpath)
            if m.get("temp_c") is not None:
                self.set_metric(id=("Interface | DOM | Temperature", mpath),
                                metric="Interface | DOM | Temperature",
                                path=ipath,
                                value=float(m["temp_c"]),
                                multi=True)
            if m.get("voltage_v") is not None:
                self.set_metric(id=("Interface | DOM | Voltage", mpath),
                                metric="Interface | DOM | Voltage",
                                path=ipath,
                                value=float(m["voltage_v"]),
                                multi=True)
            if m.get("optical_rx_dbm") is not None:
                self.set_metric(id=("Interface | DOM | RxPower", mpath),
                                metric="Interface | DOM | RxPower",
                                path=ipath,
                                value=float(m["optical_rx_dbm"]),
                                multi=True)
            if m.get("optical_rx_dbm_cpe") is not None:
                self.set_metric(id=("Interface | DOM | RxPower", mpath),
                                metric="Interface | DOM | RxPower",
                                path=["", "", "", cc["interface"], cc["id"]],
                                value=float(m["optical_rx_dbm_cpe"]
                                            if "," not in m["optical_rx_dbm_cpe"] else
                                            m["optical_rx_dbm_cpe"].split(",")[0]),
                                multi=True)
            if m.get("current_ma") is not None:
                self.set_metric(id=("Interface | DOM | Bias Current", mpath),
                                metric="Interface | DOM | Bias Current",
                                path=ipath,
                                value=float(m["current_ma"]),
                                multi=True)
            if m.get("optical_tx_dbm") is not None:
                self.set_metric(id=("Interface | DOM | TxPower", mpath),
                                metric="Interface | DOM | TxPower",
                                path=ipath,
                                value=float(m["optical_tx_dbm"]),
                                multi=True)

        self.cli("quit")
        self.cli("quit")
