# ---------------------------------------------------------------------
# Juniper.JUNOS.get_chassis_id
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
    name = "Juniper.JUNOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GETNEXT_OIDS = {"SNMP": ["1.3.6.1.4.1.2636.3.40.1.4.1.1.1.4"]}

    rx_range = re.compile(
        r"(?P<type>Public|Private) base address\s+(?P<mac>\S+)\s+"
        r"(?P=type) count\s+(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE,
    )
    rx_range2 = re.compile(
        r"^\s+Base address\s+(?P<mac>\S+)\s*\n^\s+Count\s+(?P<count>\d+)", re.MULTILINE
    )
    rx_lldp = re.compile(r"^\s+Chassis ID\s+:\s+(?P<mac>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show chassis mac-addresses")
        macs = []
        for _, mac, count in self.rx_range.findall(v):
            mac = MAC(mac)
            if not int(mac):
                # Check if 00:00:00:00:00
                continue
            f, t = str(mac), mac.shift(int(count) - 1)
            if macs and MAC(f).shift(-1) == macs[-1][1]:
                macs[-1][1] = t
            else:
                macs += [[f, t]]
        # Found in some oldest switches
        if not macs and self.rx_range2.search(v):
            match = self.rx_range2.search(v)
            base = match.group("mac")
            count = int(match.group("count"))
            if MAC(base):
                return [{"first_chassis_mac": base, "last_chassis_mac": MAC(base).shift(count - 1)}]
        try:
            # Found in ex4550-32f JUNOS 15.1R7-S7.1
            # Chassis ID MAC somehow differs from `Public base address`
            v = self.cli("show lldp local-information", cached=True)
            match = self.rx_lldp.search(v)
            if match:
                macs += [[match.group("mac"), match.group("mac")]]
        except self.CLISyntaxError:
            # Found in m7i JUNOS 8.5R4.3
            pass
        return [{"first_chassis_mac": f, "last_chassis_mac": t} for f, t in macs]
