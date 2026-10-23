# ---------------------------------------------------------------------
# Nateks.FlexGainACE24.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Nateks.FlexGainACE24.get_version"
    cache = True
    interface = IGetVersion

    # FlexGain ACE24 N.3.23.i1000.ADSL2+.A
    rx_ver = re.compile(
        r".*HwVersion         : (?P<hwversion>[^ ,]+)\n"
        r"^CPLDVersion       : (?P<cpldversion>[^ ,]+)\n"
        # r"^CPSwVersion       : (?P<cpsversion>[^ ,]+)\n"
        r".*CPSwVersion.*(?P<version>.{21,}) PRIMARY .*\n"
        r".*DPSwVersion       : (?P<dpsversion>[^ ,]+)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    # FlexGain ACE24 N.1.1.401.38
    rx_ver1 = re.compile(
        r".*HwVersion         : (?P<hwversion>[^ ,]+)\n"
        r"^CPLDVersion       : (?P<cpldversion>[^ ,]+)\n"
        r".*CPSwVersion       : (?P<version>[^ ,]+) .*\n",
        # r"^CPSwVersion\(Build\): (?P<cpsversion>[^ ,]+) \[ .*\n"
        # r".*CPSwVersion.*(?P<cpsversion>[^ ,]+) .*\n"
        # r".*DPSwVersion       : WDDI (?P<dpsversion>[^ ,]+)\n"
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    # FIX: N.1.1.401.38 has no serial and there is no way to get it?
    # rx_eeprom = re.compile(
    #  r".*SN                 : S/N: (?P<sn>[^ ,]+)\n"
    #  , re.MULTILINE | re.DOTALL | re.IGNORECASE)

    def execute(self):
        v = ""
        v = self.cli("get system info", cached=True)

        rx = self.find_re([self.rx_ver, self.rx_ver1], v)

        match = rx.search(v)

        version1 = match.group("version")

        # FIX: N.1.1.401.38 has no serial and there is no way to get it?
        # v2 = self.cli("get sys eeprom256", cached=True)
        # matcheeprom = self.re_search(self.rx_eeprom, v2)
        # platform  = version1.split(".")[3]

        return {
            "vendor": "Nateks",
            # "platform": platform,
            "platform": "FlexGain ACE24",
            # "cpsdversion": match.group("cpsversion"),
            # "dpsdversion": match.group("dpsversion"),
            "version": version1,
            # "SN": matcheeprom.group("sn"),
            "attributes": {
                "hwversion": match.group("hwversion"),
                "cpldversion": match.group("cpldversion"),
            },
        }
