# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.ISW.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table, parse_kv, ranges_to_list


class Script(BaseScript):
    """
    Extreme.XOS.get_interfaces
    """

    name = "Extreme.ISW.get_interfaces"
    interface = IGetInterfaces

    switchport_map = {
        "name": "name",
        "access mode vlan": "untagged",
        "allowed vlans": "tagged",
        "hybrid native mode vlan": "native",
        "administrative mode": "mode",
    }

    def get_ifindexes(self):
        r = {}
        v = self.cli("show snmp mib ifmib ifIndex")
        v = parse_table(v, max_width=200)
        for row in v:
            r[row[2]] = row[0]
        return r

    def get_switchport(self):
        r = {}
        v = self.cli("show interface * switchport")
        for block in v.split("\n\n"):
            if not block:
                continue
            b = parse_kv(self.switchport_map, block)
            if b["mode"] == "trunk":
                r[b["name"]] = {
                    "tagged_vlans": ranges_to_list(b["tagged"]),
                    "untagged_vlan": b["native"],
                }
            else:
                r[b["name"]] = {"tagged_vlans": [], "untagged_vlan": b["untagged"]}
        return r

    def get_ip_interfaces(self):
        r = {}
        v = self.cli("show ip interface brief")
        v = parse_table(v)
        for row in v:
            ifname = row[0]
            iftype = self.profile.get_interface_type(ifname)
            r[ifname] = {
                "name": ifname,
                "type": iftype,
                "admin_status": row[3] == "UP",
                "description": ifname,
                "oper_status": row[3] == "UP",
                "subinterfaces": [
                    {
                        "name": ifname,
                        "ipv4_addresses": [row[1]],
                        "enabled_afi": ["IPv4"],
                        "vlan_ids": [int(ifname.split()[-1])],
                    }
                ],
            }
        return r

    def execute_cli(self, **kwargs):
        interfaces = {}
        ifindexes = self.get_ifindexes()
        switchports = self.get_switchport()

        v = self.cli("show interface * status")
        v = parse_table(v)

        for row in v:
            ifname = row[0]
            iftype = self.profile.get_interface_type(ifname)
            interfaces[ifname] = {
                "name": ifname,
                "type": iftype,
                "description": ifname,
                "admin_status": row[1] == "enabled",
                "oper_status": row[6] != "Down",
                "snmp_ifindex": int(ifindexes[ifname]),
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": row[1] == "enabled",
                        "oper_status": row[6] != "Down",
                        "tagged_vlans": switchports[ifname]["tagged_vlans"],
                        "untagged_vlan": switchports[ifname]["untagged_vlan"],
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
        interfaces.update(self.get_ip_interfaces())

        return [{"interfaces": list(six.itervalues(interfaces))}]
