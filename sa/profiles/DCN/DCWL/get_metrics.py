# ----------------------------------------------------------------------
# DCN.DCWL.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
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

    @metrics(["Memory | Total"], volatile=False, access="C")  # CLI version
    def get_memory_total(self, metrics):
        with self.profile.shell(self):
            memory_info = self.cli("cat /proc/meminfo")
            for line in memory_info.splitlines():
                line = line.split(":", 1)
                if line[0] == "MemTotal":
                    memory_total = line[1].strip().split(" ")[0]
                    break
            self.set_metric(id=("Memory | Total", None), value=int(memory_total), units="byte")

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
            "Interface | Speed",
            "Interface | Status | Admin",
            "Interface | Status | Oper",
        ],
        has_capability="DB | Interfaces",
        volatile=False,
        access="C",  # CLI version
    )
    def get_interface_metrics(self, metrics):
        """
        get interface metrics
        """
        ifaces = []
        radio_metrics = self.get_radio_metrics(metrics)
        bss_metrics = self.get_bss_metrics(metrics)
        iface_metric_map = {
            "rx-bytes": "Interface | Load | In",
            "tx-bytes": "Interface | Load | Out",
            "rx-packets": "Interface | Packets | In",
            "tx-packets": "Interface | Packets | Out",
            "rx-errors": "Interface | Errors | In",
            "tx-errors": "Interface | Errors | Out",
            "iface-speed": "Interface | Speed",
            "admin-status": "Interface | Status | Admin",
            "oper-status": "Interface | Status | Oper",
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
            if "radio" in data and data["radio"] in radio_metrics:
                iface_speed = radio_metrics[data["radio"]]["interface-speed"]
            elif data["name"].startswith("eth"):
                iface_speed = 100000
            else:
                iface_speed = None
            if bss_metrics:
                if data["name"].startswith("eth"):
                    admin_status, oper_status = True, True
                elif data["name"].startswith("wlan"):
                    admin_status = bss_metrics[data["name"]]["admin"]
                    oper_status = bss_metrics[data["name"]]["oper"]
                else:
                    admin_status, oper_status = None, None
            for field, metric in iface_metric_map.items():
                if field.endswith("bytes") and metric in self.scale_x8:
                    units = "bit"
                elif field.endswith("bytes"):
                    units = "byte"
                elif field.endswith("errors") or field.endswith("packets"):
                    units = "pkt"
                else:
                    units = ""
                if metric == "Interface | Speed":
                    self.set_metric(
                        id=(metric, [f"noc::interface::{iface}"]),
                        value=iface_speed,
                        units=units,
                    )
                elif metric == "Interface | Status | Admin":
                    self.set_metric(
                        id=(metric, [f"noc::interface::{iface}"]),
                        value=admin_status,
                        units=units,
                    )
                elif metric == "Interface | Status | Oper":
                    self.set_metric(
                        id=(metric, [f"noc::interface::{iface}"]),
                        value=oper_status,
                        units=units,
                    )
                elif data.get(field) is not None:
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
            if (
                "radio" in data
                and data["radio"] in radio_metrics
                and "channel-util" in radio_metrics[data["radio"]]
            ):
                self.set_metric(
                    id=("Radio | Channel | Util", [f"noc::interface::{iface}"]),
                    value=float(radio_metrics[data["radio"]]["channel-util"]),
                    units="dBm",
                )

    def get_bss_metrics(self, metrics):
        """
        get wlan status info
        """
        b_metrics = defaultdict(dict)
        responce = self.cli("get bss all detail")
        for block in responce.split("\n\n"):
            data = dict(
                line.split(None, 1) for line in block.splitlines() if len(line.split(None, 1)) == 2
            )
            if not data:
                continue
            iface = data["radio"]  # iface names for example: wlan0, wlan1, wlan2, ...
            b_metrics[iface]["admin"] = data["global-radius"] == "on"
            b_metrics[iface]["oper"] = data["status"] == "up"
        return b_metrics

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
        """
        get radio interfaces data
        """
        r_metrics = defaultdict(dict)
        speed_dict = {
            "bg-n": "300000",
            "a-n": "300000",
            "a-c": "1300000",
            "b-g": "54000",
            "bg": "54000",
            "a": "54000",
            "b": "11000",
            "g": "54000",
            "n": "300000",
        }
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
            if data.get("mode") is not None:
                r_metrics[iface]["interface-speed"] = int(speed_dict.get(data["mode"].strip()))
        return r_metrics
