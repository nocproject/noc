# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.mac import MAC
from noc.core.mib import mib


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_interfaces"
    interface = IGetInterfaces

    rx_ipif = re.compile(
        r"IP Address\s+:\s+(?P<ip_address>\S+)\s*\nSubnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    rx_mgmt_vlan = re.compile(r"^802.1Q Management VLAN\s+: (?P<vlan>\S+)\s*\n")

    def execute(self, **kwargs):
        interfaces = []
        # Get portchannels
        portchannel_members = {}  # member -> (portchannel, type)
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)
        admin_status = {}
        for n, s in self.snmp.join_tables(
            mib["IF-MIB::ifName"], mib["IF-MIB::ifAdminStatus"]
        ):  # IF-MIB
            if n[:3] == "Aux" or n[:4] == "Vlan" or n[:11] == "InLoopBack":
                continue
            if n[:6] == "Slot0/":
                n = n[6:]
            admin_status.update({n: int(s) == 1})
        mac = {}
        for i, m in self.snmp.join_tables(
            mib["IF-MIB::ifName"], mib["IF-MIB::ifPhysAddress"]
        ):  # IF-MIB
            if i[:6] == "Slot0/":
                i = i[6:]
            mac.update({i: MAC(m)})

        # Get switchports
        for swp in self.scripts.get_switchport():
            admin = admin_status[swp["interface"]]
            ma = mac[swp["interface"]]
            name = swp["interface"]
            iface = {
                "name": name,
                "mac": ma,
                "type": "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": name,
                        "mac": ma,
                        "admin_status": admin,
                        "oper_status": swp["status"],
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            if swp["tagged"]:
                iface["subinterfaces"][0]["tagged_vlans"] = swp["tagged"]
            try:
                iface["subinterfaces"][0]["untagged_vlan"] = swp["untagged"]
            except KeyError:
                pass
            if "description" in swp:
                iface["description"] = swp["description"]
            if name in portchannel_members:
                iface["aggregated_interface"] = portchannel_members[name][0]
                if portchannel_members[name][1]:
                    iface["enabled_protocols"] += ["LACP"]
            interfaces += [iface]

        ipif = self.cli("show ipif")
        match = self.rx_ipif.search(ipif)
        if match:
            i = {
                "name": "System",
                "type": "SVI",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [
                    {
                        "name": "System",
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
            ch_id = self.scripts.get_chassis_id()
            i["mac"] = ch_id[0]["first_chassis_mac"]
            i["subinterfaces"][0]["mac"] = ch_id[0]["first_chassis_mac"]
            mgmt_vlan = 1
            sw = self.cli("show switch", cached=True)
            match = self.rx_mgmt_vlan.search(sw)
            if match:
                vlan = match.group("vlan")
                if vlan != "Disabled":
                    vlans = self.profile.get_vlans(self)
                    for v in vlans:
                        if vlan == v["name"]:
                            mgmt_vlan = int(v["vlan_id"])
                            break
            # Need hardware to testing
            i["subinterfaces"][0].update({"vlan_ids": [mgmt_vlan]})
            interfaces += [i]

        for pchn in self.scripts.get_portchannel():
            if len(pchn["members"]) == 0:
                continue
            pch = {
                "name": pchn["interface"],
                "type": "aggregated",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [
                    {
                        "name": pchn["interface"],
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            interfaces += [pch]

        return [{"interfaces": interfaces}]
