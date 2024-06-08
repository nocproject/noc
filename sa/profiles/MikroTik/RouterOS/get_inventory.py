# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_inventory"
    interface = IGetInventory

    rx_sfp = re.compile(
        r"(?:^\s+sfp-link-length-\d+um: (?P<ll>\d+)m\s*\n)?"
        r"(?:^\s+sfp-link-length-copper: (?P<copper>\d+)m\s*\n)?"
        r"^\s+sfp-vendor-name: (?P<vendor>.+)\s*\n"
        r"^\s+sfp-vendor-part-number: (?P<part_no>.+)\s*\n"
        r"^\s+sfp-vendor-revision: (?P<revision>\S+)\s*\n"
        r"^\s+sfp-vendor-serial: (?P<serial>\S+)\s*\n"
        r"(?:^\s+sfp-manufacturing-date: (?P<date>\S+)\s*\n)?"
        r"(?:^\s+sfp-wavelength: (?P<nm>\d+)nm\s*$)?",
        re.MULTILINE,
    )
    rx_rate = re.compile(r"^\s+rate: (?P<rate>\S+)\s*\n", re.MULTILINE)

    def convert_speed(self, rate: str) -> str:
        return {"1Gbps": "1000", "10Gbps": "10000"}.get(rate, "0")

    def execute_cli(self):
        i = []
        v = self.scripts.get_version()
        platform = v["platform"]
        if platform not in ["x86", "CHR"]:
            serial = self.capabilities.get("Chassis | Serial Number")
            i += [
                {
                    "type": "CHASSIS",
                    "vendor": "MikroTik",
                    "part_no": [platform],
                    "serial": serial,
                }
            ]
            eth = {}
            for n, f, r in self.cli_detail("/interface ethernet print detail without-paging"):
                iface = r["default-name"]
                eth[str(n)] = iface
            for port in range(len(eth)):
                inv = self.cli("/interface ethernet monitor " + str(port) + " once")
                rt = self.rx_rate.search(inv)
                if rt:
                    rate = rt.group("rate")
                else:
                    rate = None
                match = self.rx_sfp.search(inv)
                if match:
                    data = []
                    vendor = match.group("vendor")
                    description = match.group("part_no")
                    if vendor == "" or vendor == "OEM":
                        vendor = "NONAME"
                        part = "NoName | Transceiver | "
                        if match.group("nm"):
                            nm = int(match.group("nm"))
                        else:
                            nm = 0
                        if match.group("ll"):
                            ll = int(match.group("ll"))
                        else:
                            ll = 0
                        if match.group("copper"):
                            copper = int(match.group("copper"))
                            if copper == 3:
                                part_no = "SFP+-10G-CU3M"
                            elif copper == 1:
                                part_no = "SFP-H10GB-CU1M"
                            else:
                                part_no = part + "10G | SFP+ Twinax"
                        elif (description.startswith("SFP+") or rate == "10Gbps") and ll > 0:
                            if nm == 850:
                                part_no = part + "10G | SFP+ SR"
                            elif ll > 500 and ll <= 10000:
                                part_no = part + "10G | SFP+ LR"
                            elif ll > 10000 and ll <= 40000:
                                part_no = part + "10G | SFP+ ER"
                            elif ll > 40000:
                                part_no = part + "10G | SFP+ ZR"
                            else:
                                part_no = part + "10G | SFP+"
                        elif rate == "1Gbps":
                            if nm == 850:
                                part_no = part + "1G | SFP SX"
                            elif nm == 1310 and ll <= 10000:
                                part_no = part + "1G | SFP LX"
                            elif nm == 1310 and ll > 10000 and ll <= 40000:
                                part_no = part + "1G | SFP EX"
                            elif nm == 1550 and ll > 40000:
                                part_no = part + "1G | SFP ZX"
                            else:
                                part_no = part + "1G | SFP"
                        else:
                            part_no = part + "Unknown SFP"

                        data = [
                            {
                                "interface": "optical",
                                "attr": "tx_wavelength",
                                "value": nm,
                            },
                            {
                                "interface": "optical",
                                "attr": "rx_wavelength",
                                "value": nm,
                            },
                            {
                                "interface": "optical",
                                "attr": "bidi",
                                "value": False,
                            },
                            {
                                "interface": "optical",
                                "attr": "xwdm",
                                "value": False,
                            },
                            {
                                "interface": "optical",
                                "attr": "bit_rate",
                                "value": self.convert_speed(rate),
                            },
                            {
                                "interface": "optical",
                                "attr": "distance_max",
                                "value": ll,
                            },
                        ]
                    else:
                        part_no = description
                    x = {
                        "type": "XCVR",
                        "vendor": match.group("vendor"),
                        "serial": match.group("serial"),
                        "part_no": [part_no],
                        "number": eth[str(port)],
                        "revision": match.group("revision"),
                        "data": data,
                    }
                    date = match.group("date")
                    if date is not None:
                        dt = date.split("-")
                        year = "20" + dt[0]
                        parts = [year, dt[1], dt[2]]
                        mfd = "-".join(parts)
                        x["mfg_date"] = mfd
                    i += [x]
        return i
