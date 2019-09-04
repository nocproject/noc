# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NAG.SNR.get_inventory
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
    name = "NAG.SNR.get_inventory"
    interface = IGetInventory

    rx_media_type = re.compile(
        r"(?P<port>\S+) transceiver detail information: \s*\n"
        r"Base information:\n\s+(?P<type>\S+) found in this port, manufactured by (?P<vendor>\S+), on .+\.\s*\n"
        r"\s+Type is (?P<part_no>\S+)\.  Serial number is (?P<serial>\S+)\.\s*\n"
        r"(\s+Link length is.+\n){1,}"
        r"\s+Nominal bit rate is (?P<mbd>\d+) Mb\/s\.\s*\n"
        r"(?:\s+Laser wavelength is (?P<nm>\d+) nm\.)?",
        re.MULTILINE,
    )
    fake_vendors = ["OEM", "CISCO-FINISAR"]

    def execute(self):
        r = []
        s = self.scripts.get_version()
        revision = s["attributes"]["HW version"]
        serial = s["attributes"]["Serial Number"]
        part_no = s["platform"]
        p = {
            "type": "CHASSIS",
            "vendor": "NAG",
            "part_no": part_no,
            "revision": revision,
            "serial": serial,
            "description": "",
        }
        r += [p]
        try:
            c = self.cli("show transceiver detail")
            for match in self.rx_media_type.finditer(c):
                vendor = match.group("vendor")
                description = match.group("part_no")
                type = match.group("type")
                mbd = int(match.group("mbd"))
                nm = match.group("nm")
                if not nm:
                    nm = 0
                else:
                    nm = int(nm)
                if vendor in self.fake_vendors:
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
                        part_no = part_no + "1G | SFP"
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
                        part_no = part_no + "10G | SFP+ Copper DAC"
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
                else:
                    part_no = vendor + " | Transceiver | " + type

                i = {
                    "type": "XCVR",
                    "number": match.group("port"),
                    "vendor": vendor,
                    "part_no": part_no,
                    "revision": "",
                    "serial": match.group("serial"),
                    "description": "%s, %dMbd, %dnm" % (description, mbd, nm),
                }
                r += [i]
        except self.CLISyntaxError:
            pass

        return r
