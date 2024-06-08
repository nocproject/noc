# ---------------------------------------------------------------------
# NAG.SNR.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "NAG.SNR.get_inventory"
    interface = IGetInventory

    rx_media_type = re.compile(
        r"Ethernet(?P<ch_id>\d+)\/(?P<port>\S+) transceiver detail information: \s*\n"
        r"Base information:\s*\n\s+(?P<type>\S+) found in this port, manufactured by (?P<vendor>\S+), on (?P<mf_m>\S+) (?P<mf_d>\d+) (?P<mf_y>\d+)\.\s*\n"
        r"\s+Type is (?P<part_no>\S+)\.  Serial number is (?P<serial>\S+)\.\s*\n"
        r"(\s+Link length is.+\n){1,}"
        r"\s+Nominal bit rate is (?P<mbd>\d+) Mb\/s\.\s*\n"
        r"(?:\s+Laser wavelength is (?P<nm>\d+) nm\.)?",
        re.MULTILINE,
    )
    rx_stack = re.compile(
        r"^(Software package |Local software )version\s+:\s(?P<software>\S+)\s*\n"
        r"^Bootrom version\s+:\s(?P<bootrom>\S+)\s*\n"
        r"^CPLD.+\n"
        r"^Hardware version\s+:\s(?P<hardware>\S+)\s*\n"
        r"^Serial number\s+:\s(?P<serial>\S+)\s*\n"
        r"^Manufacture date\s+:\s(?P<mfg_date>\S+)\s*\n",
        re.MULTILINE,
    )
    month = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }

    def execute_cli(self, **kwargs):
        r = []
        s = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        revision = self.capabilities.get("Chassis | HW Version")
        part_no = s["platform"]
        vendor = s["vendor"]
        if self.is_foxgate_cli:
            r = [
                {
                    "type": "CHASSIS",
                    "vendor": vendor,
                    "part_no": part_no,
                    "revision": revision,
                    "serial": serial,
                    "description": "",
                }
            ]
            r += self.get_transceivers(1)
            return r
        try:
            slot = self.cli("show slot")
        except self.CLISyntaxError:
            slot = "Invalid"
        for slot_id, match in enumerate(self.rx_stack.finditer(slot), start=1):
            mfg_date = match.group("mfg_date")
            date = mfg_date.replace("/", "-")
            r += [
                {
                    "type": "CHASSIS",
                    "number": slot_id,
                    "vendor": vendor,
                    "mfg_date": date,
                    "part_no": part_no,
                    "revision": match.group("hardware"),
                    "serial": match.group("serial"),
                    "description": "",
                }
            ]
            r += self.get_transceivers(slot_id)
        # Some devices do not have `show slot` command
        if not r:
            r = [
                {
                    "type": "CHASSIS",
                    "vendor": vendor,
                    "part_no": part_no,
                    "revision": revision,
                    "serial": serial,
                    "description": "",
                }
            ]
            r += self.get_transceivers(1)
        return r

    def convert_t_data_to_speed(self, mbd: int, description: str = "") -> str:
        speed = "0"
        if mbd > 1000 and mbd <= 1300:
            speed = "1000"
        elif mbd > 10000 and mbd <= 10300:
            speed = "10000"
        elif description.startswith("40G"):
            speed = "40000"
        return speed

    def get_transceivers(self, slot_id):
        out = []
        try:
            c = self.cli("show transceiver detail", cached=True)
        except self.CLISyntaxError:
            return out
        for match in self.rx_media_type.finditer(c):
            description = match.group("part_no")
            mbd = int(match.group("mbd"))
            nm = match.group("nm")
            ch_id = int(match.group("ch_id"))
            if ch_id == slot_id:
                nm = nm or 0
                nm = int(nm)
                vendor = "NONAME"
                part_no = "NoName | Transceiver | "
                if mbd == 1300 and nm == 1310:
                    part_no = part_no + "1G | SFP BXU"
                elif mbd == 1300 and nm == 1550:
                    part_no = part_no + "1G | SFP BXD"
                elif mbd == 1200 and nm == 1310:
                    part_no = part_no + "1G | SFP BX10U"
                elif mbd >= 1200 and nm == 1490:
                    part_no = part_no + "1G | SFP BX10D"
                elif mbd == 10300 and nm == 0 and description.startswith("unkn"):
                    part_no = part_no + "10G | SFP+ Twinax"
                elif mbd == 10300 and description.startswith("10G"):
                    if description.endswith(tuple([" ER", "-ER"])):
                        part_no = part_no + "10G | SFP+ ER"
                    elif description.endswith(tuple([" LR", "-LR"])):
                        part_no = part_no + "10G | SFP+ LR"
                    elif description.endswith(tuple([" SR", "-SR"])):
                        part_no = part_no + "10G | SFP+ SR"
                    elif description.endswith(tuple([" ZR", "-ZR"])):
                        part_no = part_no + "10G | SFP+ ZR"
                    else:
                        part_no = part_no + "10G | SFP+"
                elif mbd == 12000 and nm == 0:
                    part_no = part_no + "10G | SFP+ Twinax"
                elif mbd >= 1000 and mbd <= 1300 and nm == 0:
                    if description.endswith(tuple([" EX", "-EX"])):
                        part_no = part_no + "1G | SFP EX"
                    elif description.endswith(tuple([" LH", "-LH"])):
                        part_no = part_no + "1G | SFP LH"
                    elif description.endswith(tuple([" LX", "-LX"])):
                        part_no = part_no + "1G | SFP LX"
                    elif description.endswith(tuple([" SX", "-SX"])):
                        part_no = part_no + "1G | SFP SX"
                    elif description.endswith(tuple([" T", "-T"])):
                        part_no = part_no + "1G | SFP T"
                    elif description.endswith(tuple([" TX", "-TX"])):
                        part_no = part_no + "1G | SFP TX"
                    elif description.endswith(tuple([" ZX", "-ZX"])):
                        part_no = part_no + "1G | SFP ZX"
                    else:
                        part_no = part_no + "1G | SFP"
                elif mbd == 100 and nm == 1310:
                    part_no = part_no + "100M | SFP BX100U"
                elif mbd == 100 and nm == 1550:
                    part_no = part_no + "100M | SFP BX100D"
                elif description.startswith("40G"):
                    part_no = part_no + "40G | QSFP+"
                else:
                    part_no = part_no + "Unknown SFP"
                mf_m = match.group("mf_m")

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
                        "value": self.convert_t_data_to_speed(mbd, description),
                    },
                ]

                if mf_m == "(null)":
                    i = {
                        "type": "XCVR",
                        "number": "Ethernet1/" + match.group("port"),
                        "vendor": vendor,
                        "part_no": part_no,
                        "serial": match.group("serial"),
                        "description": "%s, %dMbd, %dnm" % (description, mbd, nm),
                        "data": data,
                    }
                else:
                    mf_mon = self.month.get(mf_m)
                    mf_parts = [match.group("mf_y"), mf_mon, match.group("mf_d")]
                    mf_date = "-".join(mf_parts)
                    i = {
                        "type": "XCVR",
                        "number": "Ethernet1/" + match.group("port"),
                        "vendor": vendor,
                        "part_no": part_no,
                        "mfg_date": mf_date,
                        "serial": match.group("serial"),
                        "description": "%s, %dMbd, %dnm" % (description, mbd, nm),
                        "data": data,
                    }
                out += [i]

        return out
