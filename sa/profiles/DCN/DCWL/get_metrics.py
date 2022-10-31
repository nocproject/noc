# ----------------------------------------------------------------------
# DCN.DCWL.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
import codecs

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.core.validators import is_ipv4
from noc.core.comp import smart_text


class Script(GetMetricsScript):
    name = "DCN.DCWL.get_metrics"
    scale_x8 = {"Interface | Load | In", "Interface | Load | Out"}  # Scale 8 metric type

    @metrics(["CPU | Usage"], volatile=False, access="C")  # CLI version
    def get_cpu_metrics(self, metrics):
        with self.profile.shell(self):
            c = self.cli("cat /proc/loadavg")
            if c:
                cpu = c.split(" ")[1].strip()
                self.set_metric(id=("CPU | Usage", None), value=round(float(cpu) + 0.5), units="%")

    @metrics(["Memory | Usage"], volatile=False, access="C")  # CLI version
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
                    self.set_metric(id=("Memory | Usage", None), value=memory, units="%")

    @metrics(["Check | Result", "Check | RTT"], volatile=False, access="C")  # CLI version
    def get_avail_metrics(self, metrics):
        if not self.credentials["path"]:
            return
        for ip in self.credentials["path"].split(","):
            if is_ipv4(ip.strip()):
                result = self.scripts.ping(address=ip)
                self.set_metric(
                    id=("Check | Result", None),
                    metric="Check | Result",
                    labels=(
                        "noc::diagnostic::REMOTE_PING",
                        "noc::check::name::ping",
                        f"noc::check::arg0::{ip}",
                        "noc::check_name::ping",
                        f"noc::check_id::{ip}",
                    ),
                    value=bool(result["success"]),
                    multi=True,
                )
                if result["success"] and "avg" in result:
                    self.set_metric(
                        id=("Check | RTT", None),
                        metric="Check | RTT",
                        labels=(
                            "noc::diagnostic::REMOTE_PING",
                            "noc::check::name::ping",
                            f"noc::check::arg0::{ip}",
                            "noc::check_name::ping",
                            f"noc::check_id::{ip}",
                        ),
                        value=bool(result["avg"]),
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
            "Interface | Load | In",
            "Interface | Load | Out",
            "Interface | Packets | In",
            "Interface | Packets | Out",
            "Interface | Errors | In",
            "Interface | Errors | Out",
        ],
        has_capability="DB | Interfaces",
        volatile=False,
        access="C",  # CLI version
    )
    def get_interface_metrics(self, metrics):
        ifaces = []
        radio_metrics = self.get_radio_metrics(metrics)
        iface_metric_map = {
            "rx-bytes": "Interface | Load | In",
            "tx-bytes": "Interface | Load | Out",
            "rx-packets": "Interface | Packets | In",
            "tx-packets": "Interface | Packets | Out",
            "rx-errors": "Interface | Errors | In",
            "tx-errors": "Interface | Errors | Out",
        }
        c = self.cli("get interface all detail")
        for block in c.split("\n\n"):
            ifaces += [
                dict(
                    line.split(None, 1)
                    for line in block.splitlines()
                    if len(line.split(None, 1)) == 2
                )
            ]
        self.get_beacon_iface(ifaces)
        for data in ifaces:
            if data.get("status", "up") == "down":
                # Skip if interface is down
                continue
            if "ssid" in data:
                ssid = data["ssid"].strip().replace(" ", "").replace("Managed", "")
                if ssid.startswith("2a2d"):
                    # 2a2d - hex string
                    ssid = smart_text(codecs.decode(ssid, "hex"))
                iface = f'{data["name"]}.{ssid}'
            else:
                iface = data["name"]
            for field, metric in iface_metric_map.items():
                if metric.endswith("bytes") and metric in self.scale_x8:
                    units = "bit"
                elif metric.endswith("bytes"):
                    units = "byte"
                else:
                    units = "pkt"
                if data.get(field) is not None:
                    self.set_metric(
                        id=(metric, [f"noc::interface::{iface}"]),
                        value=float(data[field]),
                        type="counter",
                        # scale=8 if metric in self.scale_x8 else 1,
                        units=units,
                    )
            # LifeHack. Set Radio interface metrics to SSID
            if "radio" in data and data["radio"] in radio_metrics:
                self.set_metric(
                    id=("Radio | TxPower", [f"noc::interface::{iface}"]),
                    value=float(radio_metrics[data["radio"]]["tx-power"]),
                    units="dBm",
                )
            if "radio" in data and data["radio"] in radio_metrics:
                self.set_metric(
                    id=("Radio | Channel | Util", [f"noc::interface::{iface}"]),
                    value=float(radio_metrics[data["radio"]]["channel-util"]),
                    units="dBm",
                )

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
            if data.get("tx-power") is not None:
                self.set_metric(
                    id=("Radio | TxPower", [f"noc::interface::{iface}"]),
                    # Max TxPower 27dBm, convert % -> dBm
                    value=(27 / 100) * int(data["tx-power"].strip()),
                    units="dBm",
                )
                r_metrics[iface]["tx-power"] = (27 / 100) * int(data["tx-power"].strip())
            if data.get("channel-util") is not None:
                self.set_metric(
                    id=("Radio | Channel | Util", [f"noc::interface::{iface}"]),
                    value=data["channel-util"],
                )
                r_metrics[iface]["channel-util"] = (27 / 100) * int(data["channel-util"].strip())
        return r_metrics
