# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_inventory
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
    name = "Zhone.Bitstorm.get_inventory"
    interface = IGetInventory

    rx_card = re.compile(
        r"^(?P<part_no>\S+ [Cc]ard)\s*\n"
        r"(^HW Rev\s+(?P<revision>\S+)\s*\n)?"
        r"(^PLD Rev\s+\S+\s*\n)?"
        r"(^Serial Number(?P<serial>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_card1 = re.compile(
        r"^Slot\s+(?P<number>\d+).*\n"
        r"^Main Card Name\s+(?P<descr>.+?)\s*\n"
        r"^Main Card Model Number\s+(?P<part_no>\S+)\s*\n"
        r"^Main Card Serial Number\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_child_card = re.compile(
        r"^Child Card Model Number\s+(?P<part_no>\S+)\s*\n"
        r"^Child Card Serial Number\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )

    PLATFORMS = {
        "4214-A1-520": "24p ReachDSL, T1 MLPPP, No Splitters",
        "4214-A1-522": "24p ReachDSL, E1 MLPPP, No Splitters",
        "4214-A1-530": "24p ReachDSL, T1 MLPPP, w/Internal Splitters",
        "4214-A1-531": "24p ReachDSL, E1 MLPPP, w/Internal 600ohm Splitters",
        "4214-A1-532": "24p ReachDSL, E1 MLPPP, w/Internal Splitters",
        "4219-A2-520": "24p ReachDSL, GigE Uplink, No Splitters",
        "4219-A2-530": "24p ReachDSL, GigE Uplink, w/Internal Splitters",
        "4219-A2-531": "24p ReachDSL, GigE Uplink, w/Internal 600 ohm Splitters",
        "4224-A1-520": "24p ADSL2+, T1 MLPPP Uplink, No Splitters",
        "4224-A1-522": "24p ADSL2+, E1 MLPPP Uplink, No Splitters",
        "4224-A1-530": "24p ADSL2+, T1 MLPPP Uplink, w/Internal Splitters",
        "4224-A1-531": "24p ADSL2+, E1 MLPPP Uplink, w/Internal 600ohm Splitters",
        "4224-A1-532": "24p ADSL2+, E1 MLPPP Uplink, w/Internal Splitters",
        "4229-A3-520": "24p ADSL2+, GigE Uplink, No Splitters",
        "4229-A3-530": "24p ADSL2+, GigE Uplink, w/Internal Splitters",
        "4229-A3-531": "24p ADSL2+, GigE Uplink, w/Internal 600 ohm Splitters",
        "4234-A1-522": "24p ADSL2+, E1 MLPPP Uplink, No Splitters",
        "4234-A1-532": "24p ADSL2+, E1 MLPPP Uplink, w/Internal ISDN Splitter",
        "4239-A3-520": "24p ADSL2+ Annex B, GigE Uplink, No Splitters",
        "4239-A3-532": "24p ADSL2+ Annex B, GigE Uplink, w/Internal ISDN Splitters",
    }

    def execute_cli(self):
        v = self.scripts.get_version()
        r = {"type": "CHASSIS", "vendor": "ZHONE", "part_no": [v["platform"]]}
        serial = self.capabilities.get("Chassis | Serial Number")
        if serial:
            r["serial"] = serial
        if self.PLATFORMS.get(v["platform"]):
            r["description"] = self.PLATFORMS.get(v["platform"])
        res = [r]
        v = self.cli("show system information", cached=True)
        for match in self.rx_card.finditer(v):
            r = {"type": "CARD", "vendor": "ZHONE", "part_no": [match.group("part_no")]}
            if match.group("revision"):
                r["revision"] = match.group("revision")
            if match.group("serial"):
                r["serial"] = match.group("serial")
            res += [r]
        if "Paradyne DSLAM" in v or "Zhone DSLAM" in v:
            v = self.cli("show slot-information", cached=True)
            for card in v.split("\n\n"):
                match = self.rx_card1.search(card)
                r = {
                    "number": match.group("number"),
                    "type": "CARD",
                    "vendor": "ZHONE",
                    "part_no": [match.group("part_no")],
                    "serial": match.group("serial"),
                    "description": match.group("descr"),
                }
                res += [r]
                match = self.rx_child_card.search(card)
                if match:
                    r = {
                        "type": "CHILDCARD",
                        "vendor": "ZHONE",
                        "part_no": [match.group("part_no")],
                        "serial": match.group("serial"),
                    }
                    res += [r]
        return res
