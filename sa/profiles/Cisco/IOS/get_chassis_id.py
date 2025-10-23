# ---------------------------------------------------------------------
# Cisco.IOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.IOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_small_cat = re.compile(r"^Base [Ee]thernet MAC Address\s*:\s*(?P<id>\S+)", re.MULTILINE)

    def execute_small_cat(self):
        """
        Catalyst 2960/3560/3750/3750ME/3120 on IOS SE
        Catalyst 2900 on IOS E
        Catalyst 2960 on IOS FX
        Catalyst 2950 on IOS EA
        Catalyst 3850 on IOS EX
        Catalyst 3500 on IOS WC
        Single chassis mac
        :return:
        """
        v = self.cli("show version")
        match = self.re_search(self.rx_small_cat, v)
        base = match.group("id")
        return [{"first_chassis_mac": base, "last_chassis_mac": base}]

    rx_cat4000 = re.compile(
        r"MAC Base = (?P<id>\S+).+MAC Count = (?P<count>\d+)", re.MULTILINE | re.DOTALL
    )

    def execute_cat4000(self):
        """
        Cisco Catalyst 4000/4500/4500e Series
        :return:
        """
        try:
            v = self.cli("show idprom chassis")
        except self.CLISyntaxError:
            v = self.cli("show idprom supervisor")
        match = self.re_search(self.rx_cat4000, v)
        base = match.group("id")
        count = int(match.group("count"))
        return [{"first_chassis_mac": base, "last_chassis_mac": MAC(base).shift(count - 1)}]

    rx_cat6000 = re.compile(
        r"chassis MAC addresses:.+from\s+(?P<from_id>\S+)\s+to\s+(?P<to_id>\S+)", re.MULTILINE
    )

    def execute_cat6000(self):
        """
        Cisco Catalyst 6500 Series or Cisco router 7600 Series
        :return:
        """
        v = self.cli("show catalyst6000 chassis-mac-addresses")
        match = self.re_search(self.rx_cat6000, v)
        return [
            {"first_chassis_mac": match.group("from_id"), "last_chassis_mac": match.group("to_id")}
        ]

    rx_iosxe = re.compile(
        r"Chassis MAC Address\s*:\s*(?P<mac>\S+)\s+MAC Address block size\s*:\s*(?P<count>\d+)"
    )

    def execute_IOSXE(self):
        """
        IOS XE
        :return:
        """
        v = self.cli("show diag chassis eeprom detail")
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1)) for mac, count in self.rx_iosxe.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [{"first_chassis_mac": f, "last_chassis_mac": t} for f, t in macs]

    rx_c3900 = re.compile(
        r"Chassis MAC Address\s*:\s*(?P<mac>\S+)\s*\n"
        r"MAC Address block size\s*:\s*(?P<count>\d+)",
        re.MULTILINE,
    )

    def execute_c3900(self):
        """
        Cisco ISR series
        C3900, C2951
        :return:
        """
        v = self.cli("show diag")
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1)) for mac, count in self.rx_iosxe.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [{"first_chassis_mac": f, "last_chassis_mac": t} for f, t in macs]

    rx_7200 = re.compile(r"MAC Pool Size\s+(?P<count>\d+)\s+MAC Addr Base\s+(?P<mac>\S+)")

    def execute_7200(self):
        """
        7200, 7301
        :return:
        """
        v = self.cli("show c%s00 | i MAC" % self.version["platform"][:2])
        macs = []
        for f, t in [
            (mac, MAC(mac).shift(int(count) - 1)) for count, mac in self.rx_7200.findall(v)
        ]:
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        return [{"first_chassis_mac": f, "last_chassis_mac": t} for f, t in macs]

    def execute_cli(self):
        if self.is_platform_7200:
            return self.execute_7200()
        if self.is_isr_router:
            return self.execute_c3900()
        if self.is_iosxe:
            return self.execute_IOSXE()
        if self.is_cat6000 or self.is_platform_7600:
            return self.execute_cat6000()
        if self.is_cat4000:
            return self.execute_cat4000()
        if self.is_small_cat or self.is_platform_me3x00x:
            return self.execute_small_cat()
        raise self.NotSupportedError()
