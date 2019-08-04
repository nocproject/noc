# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Eltex.WOP.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import division
from collections import defaultdict

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.lib.validators import is_ipv4


class Script(GetMetricsScript):
    name = "Eltex.WOP.get_metrics"
    scale_x8 = {"Interface | Load | In", "Interface | Load | Out"}  # Scale 8 metric type

    @metrics(["CPU | Usage"], volatile=False, access="C")  # CLI version
    def get_cpu_metrics(self, metrics):
        c = self.cli("get monitoring cpu-usage")
        cpu = c.strip()
        self.set_metric(id=("CPU | Usage", None), value=round(float(cpu) + 0.5))

    @metrics(["Memory | Usage"], volatile=False, access="C")  # CLI version
    def get_memory_metrics(self, metrics):
        c = self.cli("get monitoring memory-usage")
        memory = c.strip()
        self.set_metric(id=("Memory | Usage", None), value=memory)

    @metrics(["Environment | Temperature"], volatile=False, access="C")  # CLI version
    def get_temperature_metrics(self, metrics):
        c = self.cli("get monitoring temperature")
        temperature = c.strip()
        self.set_metric(id=("Environment | Temperature", None), value=temperature)

    @metrics(["Check | Result", "Check | RTT"], volatile=False, access="C")  # CLI version
    def get_avail_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        check_id = 999
        check_rtt = 998
        for m in metrics:
            if m.metric == "Check | Result":
                check_id = m.id
            if m.metric == "Check | RTT":
                check_rtt = m.id
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
                self.set_metric(
                    id=check_id,
                    metric="Check | Result",
                    path=("ping", ip),
                    value=bool(result["success"]),
                    multi=True,
                )
                if result["success"] and check_rtt != 998:
                    self.set_metric(
                        id=check_rtt,
                        metric="Check | RTT",
                        path=("ping", ip),
                        value=bool(result["success"]),
                    )

    def get_beacon_iface(self, ifaces):
        """
        Beacon iface. Add Status and mapping for SSID <-> Radio interface
        :param ifaces:
        :return:
        """
        for s in ifaces:
            if "bss" not in s:
                continue
            v = self.cli("get bss %s detail" % s["bss"])
            for block in v.split("\n\n"):
                data = dict(
                    line.split(None, 1)
                    for line in block.splitlines()
                    if len(line.split(None, 1)) == 2
                )
                if "status" not in data:
                    continue
                s["status"] = data["status"]
                s["radio"] = data["radio"]

    @metrics(
        [
            "Radio | TxPower",
            "Radio | Quality",
            "Radio | Channel | Util",
            "Radio | Channel | Free",
            "Radio | Channel | Busy",
            "Radio | Channel | TxFrame",
            "Radio | Channel | RxFrame",
        ],
        has_capability="DB | Interfaces",
        volatile=True,
        access="C",  # CLI version
    )
    def get_radio_metrics(self, metrics):
        r_metrics = defaultdict(dict)
        w = self.cli("get radio all detail")
        for block in w.split("\n\n"):
            data = dict(
                line.split(None, 1) for line in block.splitlines() if len(line.split(None, 1)) == 2
            )
            if not data:
                continue
            iface = data["name"].strip()
            if data.get("tx-power-dbm") is not None:
                self.set_metric(
                    id=("Radio | TxPower", ["", "", "", iface]),
                    # Max TxPower 27dBm, convert % -> dBm
                    value=int(data["tx-power-dbm"].strip()),
                )
                r_metrics[iface]["tx-power"] = int(data["tx-power-dbm"].strip())
            if data.get("channel-util") is not None:
                self.set_metric(
                    id=("Radio | Channel | Util", ["", "", "", iface]), value=data["channel-util"]
                )
                r_metrics[iface]["channel-util"] = (27 / 100) * int(data["channel-util"].strip())
        return r_metrics
