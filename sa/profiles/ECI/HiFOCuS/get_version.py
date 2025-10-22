# ---------------------------------------------------------------------
# ECI.HiFOCuS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    """
    shelfType:rs
    1-SAM_120
    2-SAM_240
    3-SAM_480
    4-FLEX_RAM
    7-SAM_960
    11-HF_M82
    12-HF_M41
    14-HF_M82C
    15-HF_M61
    19-SAM_960E
    20-MINI_RAM_24V
    21-GPOWER_RAM_24V
    22-GPOWER_RAM_48V
    23-HF F152
    24-HF F61
    25-HF F52
    """

    name = "ECI.HiFOCuS.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False
    always_prefer = "S"

    rx_platform = re.compile(r"\|\|\s+0\s+\|\|\s+(?P<platform>.+)\s*\n")

    rx_ver = re.compile(
        r"^\s*NI CARD TYPE\s+: (?P<cardtype>.+)\n^\s*NI SW VERSION NAME\s+: (?P<version>.+)\n",
        re.MULTILINE,
    )

    shelf_type_map = {
        1: "SAM_120",
        2: "SAM_240",
        3: "SAM_480",
        4: "FLEX_RAM",
        7: "SAM_960",
        8: "HF_M82",
        11: "HF_M82",
        12: "HF_M41",
        14: "HF_M82C",
        15: "HF_M61",
        19: "SAM_960E",
        20: "MINI_RAM_24V",
        21: "GPOWER_RAM_24V",
        22: "GPOWER_RAM_48V",
        23: "HF F152",
        24: "HF F61",
        25: "HF F52",
    }

    def execute_snmp(self, **kwargs):
        # Get shelf
        r = self.snmp.getnext("1.3.6.1.4.1.1286.1.3.3.5.2.3.1.5", only_first=True)
        oid, shelf_type = r[0]
        # Use shelf type as platform
        platform = self.shelf_type_map.get(int(shelf_type))
        r = self.snmp.getnext("1.3.6.1.4.1.1286.1.3.3.1.1.2", only_first=True)
        oid, version = r[0]
        return {
            "vendor": "ECI",
            "platform": platform,
            "version": version,
            # "attributes": {"cardtype": cardtype},
        }

    def execute_cli(self, **kwargs):
        try:
            c = self.cli("EXISTSH ALL")
            match = self.rx_platform.search(c)
            platform = match.group("platform")
        except self.CLISyntaxError:
            raise NotImplementedError
        match = self.rx_ver.search(self.cli("ver"))
        version = match.group("version").strip()
        cardtype = match.group("cardtype").strip()

        return {
            "vendor": "ECI",
            "platform": platform,
            "version": version,
            "attributes": {"cardtype": cardtype},
        }
