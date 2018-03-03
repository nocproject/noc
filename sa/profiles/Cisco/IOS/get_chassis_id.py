# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.IOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    #
    # Catalyst 2960/3560/3750/3750ME/3120 on IOS SE
    # Catalyst 2900 on IOS E
    # Catalyst 2960 on IOS FX
    # Catalyst 2950 on IOS EA
    # Catalyst 3850 on IOS EX
    # Catalyst 3500 on IOS WC
    # Single chassis mac
    #
    rx_small_cat = re.compile(
        r"^Base [Ee]thernet MAC Address\s*:\s*(?P<id>\S+)",
        re.MULTILINE
    )

    @BaseScript.match(version__regex=r"SE|EA|EZ|FX|EX|EY|E|WC")
    def execute_small_cat(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_small_cat, v)
        base = match.group("id")
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }]

    #
    # Cisco Catalyst 4000/4500/4500e Series
    #
    rx_cat4000 = re.compile(
        r"MAC Base = (?P<id>\S+).+MAC Count = (?P<count>\d+)",
        re.MULTILINE | re.DOTALL
    )

    @BaseScript.match(version__regex=r"SG|\d\d\.\d\d\.\d\d\.E|EWA")
    def execute_cat4000(self):
        try:
            v = self.cli("show idprom chassis")
        except self.CLISyntaxError:
            v = self.cli("show idprom supervisor")
        match = self.re_search(self.rx_cat4000, v)
        base = match.group("id")
        count = int(match.group("count"))
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": MAC(base).shift(count - 1)
        }]

    #
    # Cisco Catalyst 6500 Series or Cisco router 7600 Series
    #
    rx_cat6000 = re.compile(
        r"chassis MAC addresses:.+from\s+(?P<from_id>\S+)\s+to\s+"
        r"(?P<to_id>\S+)",
        re.MULTILINE
    )

    @BaseScript.match(version__regex=r"S[YXR]")
    def execute_cat6000(self):
        v = self.cli("show catalyst6000 chassis-mac-addresses")
        match = self.re_search(self.rx_cat6000, v)
        return [{
            "first_chassis_mac": match.group("from_id"),
            "last_chassis_mac": match.group("to_id")
        }]

    #
    # IOS XE
    #
    rx_iosxe = re.compile(
        r"Chassis MAC Address\s*:\s*(?P<mac>\S+)\s+"
        r"MAC Address block size\s*:\s*(?P<count>\d+)"
    )

    @BaseScript.match(platform__regex=r"ASR100[0-6]")
    def execute_IOSXE(self):
        v = self.cli("show diag chassis eeprom detail")
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1))
            for mac, count in self.rx_iosxe.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [
            {
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in macs
        ]

    #
    # C3900, C2951
    #
    rx_c3900 = re.compile(
        r"Chassis MAC Address\s*:\s*(?P<mac>\S+)\s*\n"
        r"MAC Address block size\s*:\s*(?P<count>\d+)",
        re.MULTILINE
    )

    #
    # Cisco ISR series
    #
    @BaseScript.match(platform__regex=r"^(19\d\d|29\d\d|39\d\d)$")
    def execute_c3900(self):
        v = self.cli("show diag")
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1))
            for mac, count in self.rx_iosxe.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [
            {
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in macs
        ]

    #
    # 7200, 7301
    #
    rx_7200 = re.compile(
        r"MAC Pool Size\s+(?P<count>\d+)\s+MAC Addr Base\s+(?P<mac>\S+)"
    )

    @BaseScript.match(platform__regex=r"7200|7301")
    def execute_7200(self):
        v = self.cli("show c%s | i MAC" % self.version["platform"])
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1))
            for count, mac in self.rx_7200.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [
            {
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in macs
        ]

    #
    # Other
    #
    @BaseScript.match()
    def execute_not_supported(self):
        raise self.NotSupportedError()
