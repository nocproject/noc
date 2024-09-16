# ---------------------------------------------------------------------
# MikroTik.SwOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "MikroTik.SwOS.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        links = self.profile.parseBrokenJson(self.http.get("/link.b", cached=True, eof_mark=b"}"))
        macs = self.profile.parseBrokenJson(self.http.get("/!dhost.b", cached=True, eof_mark=b"}"))
        if links.get("prt"):
            prt = int(links["prt"], 16)
            sfp = int(links.get("sfp", "0x0"), 16)
            sfpo = int(links.get("sfpo", "0x0"), 16)
        elif self.is_platform_6port1sfp:
            prt = 6
            sfp = 1
            sfpo = 5
        if sfpo + sfp != prt:
            raise self.UnexpectedResultError("prt=%d sfp=%d sfpo=%d" % (prt, sfp, sfpo))
        ports = []
        for port in range(1, prt + 1):
            if port <= sfpo:
                ports.append("Port%d" % int(port))
            elif sfp > 1:
                ports.append("SFP%d" % (int(port) - sfpo))
            else:
                ports.append("SFP")

        for record in macs:
            iface_num = int(record["prt"], 16)
            if self.is_platform_6port1sfp:
                for i in range(8):
                    if (iface_num >> i) & 1:
                        iface_num = i
                        break
            vlan_id = int(record["vid"], 16)
            if vlan_id == 0:  # MikroTik specific
                vlan_id = 1
            r += [
                {
                    "vlan_id": vlan_id,
                    "mac": record["adr"],
                    "interfaces": [ports[iface_num]],
                    "type": "D",
                }
            ]
        return r
