# ---------------------------------------------------------------------
# HP.ProCurve.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "HP.ProCurve.get_interfaces"
    interface = IGetInterfaces

    rx_mac = re.compile(r"Hardware Address:\s+(?P<mac>\S+)")
    rx_description = re.compile(r"Description:\s+(?P<description>.+)")
    rx_mtu = re.compile(r"The Maximum Frame Length is (?P<mtu>\d+)")
    rx_pvid = re.compile(r"PVID\s*:\s+(?P<pvid>\d+)")
    rx_iface = re.compile(
        r"^\s*(?P<iface>\S+)\s+current\sstate:\s*(?P<state>UP|DOWN)\s+(?P<admin>\(\s*Administratively\s*\))?",
    )
    rx_trunk = re.compile(
        r"^\s*(?P<iface>\S+)\s*\|\s*(?P<descr>.+?)\s(?P<type>\S+)\s+\|\s*(?P<agg>\S+)\s+(?P<proto>\S+)",
        re.MULTILINE,
    )

    rx_ip = re.compile(
        r"^\s*(?P<vlan_name>.+)\s*\|\s+(?P<config>Disabled|Manual|Auto)\s*(?P<address>\S+)?\s*(?P<mask>\S+)?$",
        re.MULTILINE,
    )

    def get_switchport_cli(self):
        """
        VLAN ID: 2014
        VLAN Type: static
        Route Interface: n/a
        Description: VLAN 2014
        Name: YADRO
        Tagged   Ports:
           Trk1      Trk2      Trk3
           Trk4      Trk5      Trk24
        Untagged Ports:
           13
        """

        v = self.cli("display vlan all")
        vlans = []
        for vlan_block in v.split("\n\n"):
            params = {}
            param = None
            for ll in vlan_block.splitlines():
                p1, *p2 = ll.split(":")
                if not p2 and param:
                    params[param] += [x.strip() for x in p1.split()]
                    continue
                param = p1.strip()
                params[param] = [p2[0].strip()]
            vlans += [params]
        r = {}
        vlan_address = {}
        for vlan in vlans:
            if "IP Address" in vlan:
                vlan_address[vlan["VLAN ID"][0]] = {
                    "vlan": vlan["VLAN ID"][0],
                    "address": vlan["IP Address"][0],
                    "mask": vlan["Subnet Mask"][0],
                    "description": vlan["Description"][0],
                }
            for p1, p2 in [("Untagged Ports", "untagged_vlan"), ("Tagged   Ports", "tagged_vlans")]:
                if p1 not in vlan:
                    continue
                for iface in vlan[p1]:
                    if not iface or iface == "none":
                        continue
                    iface = self.profile.convert_interface_name(iface)
                    if iface not in r:
                        r[iface] = {"untagged_vlan": None, "tagged_vlans": []}
                    try:
                        if p2 == "tagged_vlans":
                            r[iface][p2] += [int(vlan["VLAN ID"][0])]
                        else:
                            r[iface][p2] = int(vlan["VLAN ID"][0])
                    except ValueError:
                        continue
        return r, vlan_address

    def execute_cli(self):
        if self.is_old_cli:
            raise NotImplementedError("Old CLI with SNMP only access")
        interfaces = {}
        switchports, addresses = self.get_switchport_cli()
        v = self.cli("show trunks")
        portchannels = set()
        for row in self.rx_trunk.finditer(v):
            ifname, descr, _, agg, lacp = row.groups()
            # ifname = self.profile.convert_interface_name(ifname)
            agg = self.profile.convert_interface_name(agg)
            if lacp == "LACP":
                portchannels.add(agg)
        v = self.cli("display interface brief")
        for row in v.splitlines()[9:]:
            ifname, status, _ = row.split(maxsplit=2)
            iftype = self.profile.get_interface_type(ifname)
            ifname, *aggregate = ifname.split("-")
            si = None
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": status != "ADM",
                "oper_status": status == "UP",
                "enabled_protocols": [],
                "subinterfaces": [],
            }
            if aggregate:
                iface["aggregated_interface"] = aggregate[0]
                if aggregate[0] in portchannels:
                    iface["enabled_protocols"] += ["LACP"]
            if ifname in switchports:
                si = {
                    "name": ifname,
                    "admin_status": status != "ADM",
                    "oper_status": status == "UP",
                    "enabled_afi": ["BRIDGE"],
                    # "mac": mac,
                    # "snmp_ifindex": self.scripts.get_ifindex(interface=name)
                }
                si.update(switchports[ifname])
            if si:
                iface["subinterfaces"].append(si)
            interfaces[ifname] = iface

        v = self.cli("display interface")
        for block in v.split("\n\n"):
            match = self.rx_iface.search(block)
            if not match:
                continue
            ifname, status, admin = match.groups()
            ifname = self.profile.convert_interface_name(ifname)
            for param, rx in [
                ("mac", self.rx_mac),
                ("mtu", self.rx_mtu),
                ("description", self.rx_description),
            ]:
                match = rx.search(block)
                if match:
                    interfaces[ifname][param] = match.groups()[0]
        # VLAN Interfaces
        for vlan in addresses.values():
            ifname = self.profile.convert_interface_name(f'VLAN{vlan["vlan"]}')
            interfaces[ifname] = {
                "name": ifname,
                "type": "SVI",
                "description": vlan["description"],
                "admin_status": True,
                "oper_status": True,
                "enabled_protocols": [],
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [IPv4(vlan["address"], netmask=vlan["mask"])],
                        "vlan_ids": [int(vlan["vlan"])],
                        # "mac": mac,
                        # "snmp_ifindex": self.scripts.get_ifindex(interface=name)
                    }
                ],
            }
        return [{"interfaces": interfaces.values()}]
