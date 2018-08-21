# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DCN.DCWL.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import division
import six
from collections import defaultdict
# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.lib.validators import is_ipv4


class Script(GetMetricsScript):
    name = "DCN.DCWL.get_metrics"

    @metrics(
        ["CPU | Usage"],
        volatile=False,
        access="C"  # CLI version
    )
    def get_cpu_metrics(self, metrics):
        with self.profile.shell(self):
            c = self.cli("cat /proc/loadavg")
            cpu = c.split(" ")[1].strip()
            self.set_metric(
                id=("CPU | Usage", None),
                value=round(float(cpu) + 0.5)
            )

    @metrics(
        ["Memory | Usage"],
        volatile=False,
        access="C"  # CLI version
    )
    def get_memory_metrics(self, metrics):
        with self.profile.shell(self):
            m = self.cli("cat /proc/meminfo")
            for mline in m.splitlines():
                mr = mline.split(":", 1)
                if mr[0] == "MemTotal":
                    mtotal = mr[1].strip().split(" ")[0]
                if mr[0] == "MemFree":
                    mfree = mr[1].strip().split(" ")[0]
                    memory = (100 / int(mtotal)) * int(mfree)
                    self.set_metric(
                        id=("Memory | Usage", None),
                        value=memory
                    )

    @metrics(
        ["Check | Result", "Check | RTT"],
        volatile=False,
        access="C"  # CLI version
    )
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
                    multi=True
                )
                if result["success"] and check_rtt != 998:
                    self.set_metric(
                        id=check_rtt,
                        metric="Check | RTT",
                        path=("ping", ip),
                        value=bool(result["success"])
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
                data = dict(line.split(None, 1) for line in block.splitlines()
                            if len(line.split(None, 1)) == 2)
                s["status"] = data["status"]
                s["radio"] = data["radio"]

    @metrics(
        ["Interface | Load | In", "Interface | Load | Out",
         "Interface | Packets | In", "Interface | Packets | Out",
         "Interface | Errors | In", "Interface | Errors | Out"],
        has_capability="DB | Interfaces",
        volatile=False,
        access="C"  # CLI version
    )
    def get_interface_metrics(self, metrics):
        ifaces = []
        radio_metrics = self.get_radio_metrics(metrics)
        iface_metric_map = {"rx-bytes": "Interface | Load | In",
                            "tx-bytes": "Interface | Load | Out",
                            "rx-packets": "Interface | Packets | In",
                            "tx-packets": "Interface | Packets | Out",
                            "rx-errors": "Interface | Errors | In",
                            "tx-errors": "Interface | Errors | Out"}
        c = self.cli("get interface all detail")
        for block in c.split("\n\n"):
            ifaces += [dict(line.split(None, 1) for line in block.splitlines()
                            if len(line.split(None, 1)) == 2)]
        self.get_beacon_iface(ifaces)
        for data in ifaces:
            if data.get("status", "up") == "down":
                # Skip if interface is down
                continue
            if "ssid" in data:
                ssid = data["ssid"].strip().replace(" ", "").replace("Managed", "")
                if ssid.startswith("2a2d"):
                    # 2a2d - hex string
                    ssid = ssid.decode("hex")
                iface = "%s.%s" % (data["name"], ssid)
            else:
                iface = data["name"]
            for field, metric in six.iteritems(iface_metric_map):
                if data.get(field) is not None:
                        self.set_metric(id=(metric, ["", "", "", iface]), value=data[field])
            # LifeHack. Set Radio interface metrics to SSID
            if "radio" in data and data["radio"] in radio_metrics:
                self.set_metric(id=("Radio | TxPower", ["", "", "", iface]),
                                value=radio_metrics[data["radio"]]["tx-power"])
            if "radio" in data and data["radio"] in radio_metrics:
                self.set_metric(id=("Radio | Channel | Util", ["", "", "", iface]),
                                value=radio_metrics[data["radio"]]["channel-util"])

    @metrics(
        ["Radio | TxPower", "Radio | Quality",
         "Radio | Channel | Util", "Radio | Channel | Free",
         "Radio | Channel | Busy", "Radio | Channel | TxFrame",
         "Radio | Channel | RxFrame"],
        has_capability="DB | Interfaces",
        volatile=True,
        access="C"  # CLI version
    )
    def get_radio_metrics(self, metrics):
        r_metrics = defaultdict(dict)
        w = self.cli("get radio all detail")
        for block in w.split("\n\n"):
            data = dict(line.split(None, 1) for line in block.splitlines()
                        if len(line.split(None, 1)) == 2)
            iface = data["name"].strip()
            if data.get("tx-power") is not None:
                self.set_metric(id=("Radio | TxPower", ["", "", "", iface]),
                                # Max TxPower 27dBm, convert % -> dBm
                                value=(27 / 100) * int(data["tx-power"].strip()))
                r_metrics[iface]["tx-power"] = (27 / 100) * int(data["tx-power"].strip())
            if data.get("channel-util") is not None:
                self.set_metric(id=("Radio | Channel | Util", ["", "", "", iface]), value=data["channel-util"])
                r_metrics[iface]["channel-util"] = (27 / 100) * int(data["channel-util"].strip())
        return r_metrics
