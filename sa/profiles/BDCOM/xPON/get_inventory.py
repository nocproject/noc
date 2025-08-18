# ---------------------------------------------------------------------
# BDCOM.xPON.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "BDCOM.xPON.get_inventory"
    interface = IGetInventory

    rx_brief = re.compile(
        r"^(?P<ifname>(?:g0|tg0|gpon0|epon0)/\d+)\s*(?:.+\s*(?:\n)?)?\s+"
        r"(?P<status>shutdown|down|up)\s.+?"
        r"\s(?P<transceiver>Giga-FX-SFP|Giga-Combo-FX-SFP|10Giga-FX-SFP|GPON|Giga-PON|10Giga-DAC)\s*?\n",
        re.MULTILINE,
    )
    rx_trans = re.compile(
        r"(^\s+Transceiver type\s+(?P<description>\S+)\s*\n)?"
        r"^Transceiver Info:\s*\n"
        r"^\s+SFP,(?P<plug>LC|SC|COP_PIGER),(?:(?P<nm>\d+)nm,)?(?P<xcvr_type>\S+)(?:,|\s)LOS:(?:yes|no)\s*\n"
        r"^\s+(?:SM (?P<ll>\d+)KM|CABLE (?P<lm>\d+)M)(?:\s*\n)?"
        r"\s+DDM:(?:YES|NO),Vend:(?P<vendor>\S+),PN:(?P<part_no>\S+)\s*\n"
        r"^\s+SerialNum:(?P<serial>\S+),Date:(?P<mfg_date>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_trans_old = re.compile(
        r"^Transceiver Info:\s*\n"
        r"^\s+SFP,(?P<plug>LC|SC|COP_PIGER),(?P<nm>\d+)nm,(?P<xcvr_type>\S+),[MS]M (?P<ll>\d+)K?M"
        r"\s+DDM:(?:YES|NO),Vend:(?P<vendor>\S+),SerialNum:(?P<serial>\S+),Date:(?P<mfg_date>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_descr = re.compile(r"^(?P<vendor>\S+?)\-(?P<part_no>\S+)$")

    def convert_speed(self, rate: str) -> str:
        return {
            "1000BASE-X": "1000",
            "1000BASE-FX": "1000",
            "1000BASE-LX": "1000",
            "2500BASE-FX": "2500",
            "10G-BASE-DAC": "10000",
            "10000BASE-FX-LR": "10000",
        }.get(rate, "0")

    def execute_cli(self):
        r = []
        # Chassis info
        p = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        if serial:
            p["serial"] = serial
        revision = self.capabilities.get("Chassis | HW Version")
        if revision:
            p["revision"] = revision
        r += [
            {
                "type": "CHASSIS",
                "number": None,
                "vendor": "BDCOM",
                "serial": serial,
                "description": f'{p["vendor"]} {p["platform"]}',
                "part_no": [p["platform"]],
                "revision": revision,
                "builtin": False,
            }
        ]

        # Detect transceivers
        c = self.cli("show interface brief")
        # Do not parse interfaces in which the device could not detect transceiver
        for i in self.rx_brief.finditer(c):
            ifname = i["ifname"]
            t = i["transceiver"]
            v = self.cli(f"show interface {ifname}")
            description = ""
            match = self.rx_trans.search(v)
            if match:
                part_no = match.group("part_no")
                if match.group("description"):
                    description = match.group("description").strip()
            else:
                match = self.rx_trans_old.search(v)
                # Old device do not display `part_no`
                if t in ["Giga-FX-SFP", "Giga-Combo-FX-SFP"]:
                    part_no = "SFP"
                elif t in ["10Giga-FX-SFP"]:
                    part_no = "SFP+"
                else:
                    # xPON interfaces do not display the absence of a transceiver
                    if not t in ['GPON', 'Giga-PON']:
                        self.logger.info(f"{ifname} - Unknown port type '{t}'.")
            if not match:
                # Some devices can not get transceiver info
                continue
            vendor = match.group("vendor").upper()
            if vendor in ["OEM", "NO"]:
                if description:
                    # Try to make `vendor` and `part_no` from description
                    match1 = self.rx_descr.search(description)
                    if match1:
                        vendor = match1.group("vendor").upper()
                        part_no = match1.group("part_no")
                        self.logger.info(f"{ifname} - Extract `vendor` and `part_no` from '{description}'.")

            if vendor not in ["OEM", "NO"]:
                r += [
                    {
                        "type": "XCVR",
                        "number": ifname,
                        "vendor": vendor,
                        "serial": match.group("serial"),
                        "description": description,
                        "part_no": part_no,
                        "mfg_date": match.group("mfg_date"),
                        "builtin": False,
                    }
                ]
            else:
                xcvr_type = match.group("xcvr_type")
                if xcvr_type in ["10G-BASE-DAC"]:
                    lm = int(match.group("lm"))
                    if lm == 1:
                        part_no = "NoName | Transceiver | 10G | SFP-H10GB-CU1M"
                    elif lm == 2:
                        part_no = "NoName | Transceiver | 10G | SFP+-10G-CU2M"
                    elif lm == 3:
                        part_no = "NoName | Transceiver | 10G | SFP+-10G-CU3M"
                    else:
                        part_no = "NoName | Transceiver | 10G | SFP+ Twinax"
                    r += [
                        {
                            "type": "XCVR",
                            "number": ifname,
                            "vendor": "NONAME",
                            "serial": match.group("serial"),
                            "description": description,
                            "part_no": part_no,
                            "mfg_date": match.group("mfg_date"),
                            "builtin": False,
                        }
                    ]
                    continue
                # Try to add some more info into description
                nm = match.group("nm")
                ll = match.group("ll")
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
                        "value": self.convert_speed(xcvr_type),
                    },
                    {
                        "interface": "optical",
                        "attr": "distance_max",
                        "value": ll,
                    },
                ]
                p = part_no
                part_no = "NoName | Transceiver | "
                if p == "SFP-LX-SM":
                    part_no = part_no + "1G | SFP LX"
                elif p == "SFP+":
                    if xcvr_type == "10000BASE-FX-LR":
                        part_no = part_no + "10G | SFP+ LR"
                    elif xcvr_type == "10000BASE-FX-ER":
                        part_no = part_no + "10G | SFP+ ER"
                    elif xcvr_type == "10000BASE-FX":
                        # Found in P3608-2TE
                        if match.group("plug") == "COP_PIGER":
                            part_no = part_no + "10G | SFP+ Twinax"
                        else:
                            part_no = part_no + "SFP+"
                    else:
                        self.logger.info(
                            f"{ifname} - Unknown xcvr_type '{xcvr_type}' for SFP+ `part_no`."
                        )
                        part_no = part_no + "SFP+"
                elif p == "SFP":
                    if xcvr_type == "1000BASE-LX":
                        part_no = part_no + "1G | SFP LX"
                    elif xcvr_type in ["1000BASE-X", "1000BASE-FX"]:
                        part_no = part_no + "1G | SFP"
                    else:
                        self.logger.info(
                            f"{ifname} - Unknown xcvr_type '{xcvr_type}' for SFP `part_no`."
                        )
                        part_no = part_no + "Unknown SFP"
                else:
                    self.logger.info(f"{ifname} - Unknown `part_no` '{p}'.")
                    part_no = part_no + "Unknown SFP"
                r += [
                    {
                        "type": "XCVR",
                        "number": ifname,
                        "vendor": "NONAME",
                        "serial": match.group("serial"),
                        "description": description,
                        "part_no": part_no,
                        "mfg_date": match.group("mfg_date"),
                        "builtin": False,
                        "data": data,
                    }
                ]
        return r
