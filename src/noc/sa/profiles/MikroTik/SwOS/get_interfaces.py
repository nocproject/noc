# ---------------------------------------------------------------------
# MikroTik.SwOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.script.http.base import HTTPError


class Script(BaseScript):
    name = "MikroTik.SwOS.get_interfaces"
    interface = IGetInterfaces

    PORT_RANGE = 33

    def execute(self):
        interfaces = []
        links = self.profile.parseBrokenJson(self.http.get("/link.b", cached=True, eof_mark=b"}"))
        vlans = self.profile.parseBrokenJson(self.http.get("/vlan.b", cached=True, eof_mark=b"}"))
        try:
            fwds = self.profile.parseBrokenJson(self.http.get("/fwd.b", cached=True, eof_mark=b"}"))
        except HTTPError:
            fwds = links
        sys_info = self.profile.parseBrokenJson(self.http.get("/sys.b", cached=True, eof_mark=b"}"))
        if links.get("prt"):
            prt = int(links["prt"], 16)
            sfp = int(links.get("sfp", "0x0"), 16)
            sfpo = int(links.get("sfpo", "0x0"), 16)
        elif self.is_platform_6port1sfp:
            prt = 6
            sfp = 1
            sfpo = 5
        if sfpo + sfp != prt:
            raise self.UnexpectedResultError(f"prt={int(prt)} sfp={int(sfp)} sfpo={int(sfpo)}")

        BITS = {i: 2**i for i in range(self.PORT_RANGE)}
        oper_statuses = {i: bool(int(links["lnk"], 16) & BITS[i]) for i in range(self.PORT_RANGE)}
        admin_statuses = {i: bool(int(links["an"], 16) & BITS[i]) for i in range(self.PORT_RANGE)}

        for port in range(1, prt + 1):
            if port <= sfpo:
                ifname = f"Port{int(port)}"
            elif sfp > 1:
                ifname = f"SFP{int(int(port) - sfpo)}"
            else:
                ifname = "SFP"
            if links.get("nm"):
                descr = codecs.decode(links["nm"][port - 1], "hex").decode()
            elif links.get(f"nm{int(port - 1)}"):
                descr = codecs.decode(links[f"nm{int(port - 1)}"], "hex").decode()
            else:
                descr = None
            iface = {
                "name": ifname,
                "type": "physical",
                "oper_status": oper_statuses[port - 1],
                "admin_status": admin_statuses[port - 1],
            }
            sub = {
                "name": ifname,
                "enabled_afi": ["BRIDGE"],
                "oper_status": oper_statuses[port - 1],
                "admin_status": admin_statuses[port - 1],
            }
            if descr:
                iface["description"] = descr
                sub["description"] = descr
            tagged_vlans = []
            for vlan in vlans:
                vid = int(vlan["vid"], 16)
                if vlan.get("mbr"):
                    ports = {
                        i: bool(int(vlan["mbr"], 16) & BITS[i]) for i in range(self.PORT_RANGE)
                    }
                else:
                    ports = {
                        i: bool(int(vlan["prt"][i], 16) & BITS[i]) for i in range(len(vlan["prt"]))
                    }
                if ports[port - 1]:
                    tagged_vlans.append(vid)
            untagged = int(fwds["dvid"][port - 1], 16)
            if int(fwds["vlni"][port - 1], 16) != 1:  # only tagged
                sub["untagged_vlan"] = untagged
            if int(fwds["vlni"][port - 1], 16) != 2:  # only untagged
                sub["tagged_vlans"] = tagged_vlans
            iface["subinterfaces"] = [sub]
            interfaces.append(iface)

        ip = self.profile.swap32(int(sys_info["ip"], 16))
        vlan_id = int(sys_info["avln"], 16)
        if vlan_id == 0:
            vlan_id = 1
        iface = {
            "name": "mgmt",
            "type": "SVI",
            "oper_status": True,
            "admin_status": True,
            "subinterfaces": [
                {
                    "name": "mgmt",
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [IPv4._to_prefix(ip, 32)],
                    "oper_status": True,
                    "admin_status": True,
                    "vlan_ids": vlan_id,
                }
            ],
        }
        interfaces.append(iface)

        return [{"interfaces": interfaces}]
