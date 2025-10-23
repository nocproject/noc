# ----------------------------------------------------------------------
# Alcatel.7302.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.snmp.render import render_mac
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Alcatel.7302.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(
        r"\s+base-bdg-addr\s*:\s*(?P<basemac>\S+)\s*\n^\s+sys-mac-addr\s*:\s*(?P<sysmac>\S+)",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show system shub entry misc")
        match = self.rx_id.search(v)
        basemac = match.group("basemac")
        sysmac = match.group("sysmac")
        r += [{"first_chassis_mac": basemac, "last_chassis_mac": basemac}]
        if basemac != sysmac:
            r += [{"first_chassis_mac": sysmac, "last_chassis_mac": sysmac}]

        return r

    def execute_snmp(self, **kwargs):
        macs = set()
        for oid in [
            "1.3.6.1.4.1.637.61.1.9.22.1.0",
            "1.3.6.1.4.1.637.61.1.9.22.2.0",
            "1.3.6.1.4.1.637.61.1.9.22.4.0",
        ]:
            mac = self.snmp.get(oid, display_hints={oid: render_mac})
            if not mac:
                raise NotImplementedError
            macs.add(MAC(mac))
        # Filter and convert macs
        r = [
            {"first_chassis_mac": mac, "last_chassis_mac": mac}
            for mac in sorted(macs)
            if not self.is_ignored_mac(mac)
        ]
        if not r:
            raise NotImplementedError
        return r
