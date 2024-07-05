# ---------------------------------------------------------------------
# EdgeCore.ES.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from datetime import datetime

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "EdgeCore.ES.get_inventory"
    interface = IGetInventory

    rx_trans_no = re.compile(r"\s+(?P<number>\d/\d+)\n")
    rx_trans_vend = re.compile(r"\s+Vendor Name\s+:\s+(?P<vend>\S+)\s*\n")
    rx_trans_pid = re.compile(r"\s+Vendor PN\s+:\s+(?P<pid>\S+)\s*\n")
    rx_trans_rev = re.compile(r"\s+Vendor Rev\s+:\s+(?P<rev>\S+)\s*\n")
    rx_trans_sn = re.compile(r"\s+Vendor SN\s+:\s+(?P<sn>\S+)\s*\n")
    rx_trans = re.compile(r"((?:100|1000)BASE\s+SFP)")

    rx_int_type = re.compile(
        r"(?P<int>Eth\s+\d/\d+)\n\s+Basic Information:\s+\n"
        r"\s+Port Type\s*:\s+(?P<type>\S+[\S ]*)\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    rx_trans_info = re.compile(
        r"Transceiver info:\n"
        r"\s+SFP found in this port, manufactured by\s+(?P<vendor>.+?), on\s+(?P<mfg_date>.+)\.\n"
        r"\s+Type is\s+(?P<sfp_type>.+)\.\s+Serial number is\s+(?P<serial_number>.+)\.\n"
        r"\s+Link length is\s+(?P<link_length>.+) for\s+(?P<fiber_mode>.+)\.\n"
        r"\s+Nominal bit rate is\s+(?P<bit_rate>.+)\.\n"
        r"\s+Laser wavelength is\s+(?P<wavelength>.+)\.",
        re.MULTILINE | re.IGNORECASE,
    )

    rx_iface_split = re.compile(r"Interface brief:\n", re.IGNORECASE)

    def get_transceiver_info(self, int_stat):
        r = []
        for iface in self.rx_iface_split.split(int_stat):
            if not iface:
                continue
            num = iface.split()[0].split("/")[-1]

            for t in self.rx_trans_info.finditer(iface):
                data = {
                    "type": "XCVR",
                    "number": num,
                    "vendor": t.group("vendor").strip(),
                    "part_no": "",  # no part_no in transceiver info
                    "serial": t.group("serial_number").strip(),
                    "description": "",
                }
                try:
                    mfg_date = datetime.strptime(t.group("mfg_date"), "%b %d %Y")
                    data["mfg_date"] = mfg_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
                r += [data]

        return r

    def get_chassis_sensors(self):
        r = []
        #  Power Supply state
        if self.is_platform_3510ma:
            swIndivPowerStatus_oid = "1.3.6.1.4.1.259.8.1.11.1.1.6.1.3"
        elif self.is_platform_ecs4100:
            swIndivPowerStatus_oid = "1.3.6.1.4.1.259.10.1.46.1.1.6.1.3"
        elif self.is_platform_ecs3510:
            swIndivPowerStatus_oid = "1.3.6.1.4.1.259.10.1.27.1.1.6.1.3"
        else:
            swIndivPowerStatus_oid = "1.3.6.1.4.1.259.6.10.94.1.1.6.1.3"
        for oid, v in self.snmp.getnext(swIndivPowerStatus_oid):
            #  1 - not present, 2 - power on, 3 - power off
            if v:
                num = oid.split(".")[-1]
                r += [
                    {
                        "name": f"State of PS-{num}",
                        "status": not (bool(v - 2)),
                        "description": f"State of PS-{num}",
                        "measurement": "StatusEnum",
                        "labels": [
                            "noc::sensor::placement::internal",
                            "noc::sensor::mode::flag",
                            "noc::sensor::target::supply",
                        ],
                        "snmp_oid": oid,
                    }
                ]
        return r

    def execute(self):
        objects = []
        # Chassis info
        p = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        if serial:
            p["serial"] = serial
        revision = self.capabilities.get("Chassis | HW Version")
        if revision:
            p["revision"] = revision
        objects += [
            {
                "type": "CHASSIS",
                "number": None,
                "vendor": "EDGECORE",
                "serial": serial,
                "description": f'{p["vendor"]} {p["platform"]}',
                "part_no": [p["platform"]],
                "revision": revision,
                "builtin": False,
            }
        ]

        for ob in objects:
            if ob["type"] == "CHASSIS" and self.has_snmp():
                ob.update({"sensors": self.get_chassis_sensors()})

        # Detect transceivers
        iface = self.cli("sh int status")
        if self.is_platform_4626:
            objects += self.get_transceiver_info(iface)
        for i in self.rx_int_type.finditer(iface):
            if "SFP" not in i.group("type"):
                continue
            else:
                try:
                    v = self.cli("show int transceiver " + i.group("int"))
                    for t in v.split("Ethernet"):
                        pid = ""
                        # Parsing
                        match = self.rx_trans_no.search(t)
                        if match:
                            match = self.rx_trans_pid.search(t)
                            pid = match.group("pid").strip() if match else ""
                            match = self.rx_trans_vend.search(t)
                            vendor = match.group("vend").strip() if match else "NONAME"
                            match = self.rx_trans_rev.search(t)
                            revision = match.group("rev").strip() if match else None
                            match = self.rx_trans_sn.search(t)
                            serial = match.group("sn").strip() if match else None
                            # Noname transceiver
                            if (
                                pid in ("", "N/A", "Unspecified")
                                or "\\x" in repr(pid).strip("'")
                                or "NONAME" in vendor
                            ):
                                pid = self.get_transceiver_pid(i.group("type").upper())
                            if not pid:
                                continue
                            else:
                                if "\\x" in repr(vendor).strip("'"):
                                    vendor = "NONAME"
                                if "\\x" in repr(serial).strip("'"):
                                    serial = None
                                if "\\x" in repr(revision).strip("'"):
                                    revision = None
                                # Add transceiver
                                objects += [
                                    {
                                        "type": "XCVR",
                                        "number": i.group("int").split("/")[-1],
                                        "vendor": vendor,
                                        "serial": serial,
                                        "description": "SFP Transceiver",
                                        "part_no": [pid],
                                        "revision": revision,
                                        "builtin": False,
                                    }
                                ]

                except self.CLISyntaxError:
                    pid = self.get_transceiver_pid(i.group("type").upper())
                    if not pid:
                        continue
                    else:
                        # Add transceiver
                        objects += [
                            {
                                "type": "XCVR",
                                "number": i.group("int").split("/")[-1],
                                "vendor": "NONAME",
                                "serial": None,
                                "description": "SFP Transceiver",
                                "part_no": [pid],
                                "revision": None,
                                "builtin": False,
                            }
                        ]
        return objects

    def get_transceiver_pid(self, type):
        match = self.rx_trans.search(type)
        if match:
            if "1000" in match.group(1):
                return "NoName | Transceiver | 1G | SFP"
            return "NoName | Transceiver | 100M | SFP"
        return None
