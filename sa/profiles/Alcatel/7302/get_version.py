# ----------------------------------------------------------------------
# Alcatel.7302.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.7302.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"actual-type\s*?:\s*(?P<platform>.+?)\s*$", re.MULTILINE)
    rx_slots = re.compile(r"slot count\s*:\s*(?P<slot_count>\d+)")
    rx_ver = re.compile(r".+?\/*(?P<version>[A-Za-z0-9.]+?)\s+\S+\s+active.*$", re.MULTILINE)

    port_map = {
        7: "7330",
        14: "7330",
        18: "7302",
        19: "7302",
        21: "7302",
    }  # show equipment slot for 7302 with one control plate return 19 slots

    def execute_cli(self, **kwargs):
        self.cli("environment inhibit-alarms mode batch", ignore_errors=True)
        v = self.cli("show equipment shelf")
        slots = self.rx_slots.search(v)
        v = self.cli("show software-mngt oswp")
        match_ver = self.rx_ver.search(v)
        return {
            "vendor": "Alcatel",
            "platform": self.port_map[int(slots.group("slot_count"))],
            "version": match_ver.group("version"),
        }

    rack_map = {
        "ARAM-D": "7330",
        "ALTS-T": "7302",
    }

    def execute_snmp(self, **kwargs):
        v = self.snmp.get("1.3.6.1.4.1.637.61.1.23.2.1.4.17")
        platform = self.rack_map[v]
        version = None
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.637.61.1.24.1.1.1.2"):
            if v == "NO_OSWP":
                continue
            version = v.split("/")[-1]
            break

        return {
            "vendor": "Alcatel",
            "platform": platform,
            "version": version,
        }
