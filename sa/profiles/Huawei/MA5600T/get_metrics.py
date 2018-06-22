# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from itertools import chain
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
        ["Interface | DOM | RxPower",
         "Interface | DOM | Temperature", "Interface | DOM | TxPower",
         "Interface | DOM | Voltage"],
        has_capability="DB | Interfaces",
        access="C",  # CLI version
        volatile=False
    )
    def collect_cpe_metrics(self, metrics):
        olt_dom = self.scripts.get_dom_status()  # Getting  OLT metrics
        onts = self.scripts.get_cpe()  # Getting ONT List
        self.cli("config")
        self.cli("interface gpon 0/0")  # Fix from cpes
        for cc in chain(onts, olt_dom):
            if "status" in cc and cc["status"] == "active":
                frame, slot, port, cpe_id = cc["id"].split("/")
                ipath = [cc["global_id"], "", "", "0"]
                v = self.cli("display ont optical-info %s %s" % (port, cpe_id))
                m = parse_kv(self.kv_map, v)
            elif "status" in cc:
                continue
            else:
                ipath = ["", "", "", cc["interface"]]
                m = cc
            if m.get("temp_c") is not None:
                self.set_metric(id=("Interface | DOM | Temperature", ipath),
                                value=float(m["temp_c"]))
            if m.get("voltage_v") is not None:
                self.set_metric(id=("Interface | DOM | Voltage", ipath),
                                value=float(m["voltage_v"]))
            if m.get("optical_rx_dbm") is not None:
                self.set_metric(id=("Interface | DOM | RxPower", ipath),
                                value=float(m["optical_rx_dbm"]))
            if m.get("current_ma") is not None:
                self.set_metric(id=("Interface | DOM | Bias Current", ipath),
                                value=float(m["current_ma"]))
            if m.get("optical_tx_dbm") is not None:
                self.set_metric(id=("Interface | DOM | TxPower", ipath),
                                value=float(m["optical_tx_dbm"]))
        self.cli("quit")
        self.cli("quit")
