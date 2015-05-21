# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Extreme.XOS.get_switchport"
    cache = True
    implements = [IGetSwitchport]
    TIMEOUT = 900

    rx_cont = re.compile(r",\s*$\s+", re.MULTILINE)
    rx_line = re.compile(r"\n+Port:\s+", re.MULTILINE)

    rx_descr_if = re.compile(r"^(?P<interface>\d+)\s+(?P<description>\S+).+")
    rx_snmp_name_eth = re.compile(r"^X\S+\s+Port\s+(?P<port>\d+)", re.IGNORECASE | re.DOTALL)
    rx_body_port = re.compile(r"^(?P<interface>\d+)(\S+)?", re.IGNORECASE)
    rx_body_untagvl = re.compile(r"^\s+Name:\s+\S+\s+Internal\s+Tag\s+=\s+(?P<avlan>\d+).+", re.IGNORECASE | re.DOTALL)
    rx_body_tagvl =   re.compile(r"^\s+Name:\s+\S+\s+802\.1Q\s+Tag\s+=\s+(?P<tvlan>\d+).+", re.IGNORECASE | re.DOTALL)
    rx_body_omode =   re.compile(r"^\s+Link\s+State:\s+(?P<omode>\S+).+", re.IGNORECASE | re.DOTALL)

    def get_description(self):
        r = []
        if self.snmp and self.access_profile.snmp_ro:
           try:
              for pr in self.snmp.get_tables(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.31.1.1.1.18"], bulk=True): #1.3.6.1.2.1.31.1.1.1.1
                 if ( int(pr[0])  >= 1000000):
                    continue
                 match = self.rx_snmp_name_eth.search(pr[1])
                 if match:
                    intf = match.group("port")
                    r += [{"interface": intf, "description": pr[2]}]
              return r
           except self.snmp.TimeOutError:
              pass
        # Fallback to CLI
        r = []
        s = self.cli("show ports description", cached=True)
        for l in s.split("\n"):
            match = self.rx_descr_if.match(l.strip())
            if not match:
                continue
            r += [{
                "interface": self.profile.convert_interface_name(match.group("interface")),
                "description": match.group("description")
            }]
        return r

    def execute(self):
        r = []
        # Get portchannel members
        portchannels = {}  # portchannel name -> [members]
        for p in self.scripts.get_portchannel():
            portchannels[p["interface"]] = p["members"]
        # Get descriptions
        descriptions = {}  # interface name -> description
        v = "\n"
        for p in self.get_description():
           descriptions[p["interface"]] = p["description"]
           vv = self.cli("show port %s information detail" % p["interface"])
           v = v + vv+"\n"
        # Get vlans
        known_vlans = set([vlan["vlan_id"] for vlan in
                    self.scripts.get_vlans()])
        # For each interface
        for s in self.rx_line.split(v)[1:]:
            tagged = []
            is_trunk = False
            untagged = 0
            for ss in s.strip().split("\n"):
               match = self.rx_body_port.search(ss)
               if match:
                   interface = self.profile.convert_interface_name(match.group("interface"))
               match = self.rx_body_omode.search(ss)
               if match:
                   omodeif = match.group("omode").strip()
               match = self.rx_body_untagvl.search(ss)
               if match:
                   untagged = int(match.group("avlan"))
               match = self.rx_body_tagvl.search(ss)
               if match:
                   is_trunk = True
                   tvlan = int(match.group("tvlan"))
                   tagged.append(tvlan)
            iface = {
                "interface": interface,
                "status": omodeif != "Read",
                "tagged": [v for v in tagged if v in known_vlans],
                "members": portchannels.get(interface, []),
                "802.1Q Enabled": is_trunk,
                "802.1ad Tunnel": False,
            }
            if untagged:
                iface["untagged"] = untagged
            if interface in descriptions:
                iface["description"] = descriptions[interface]

            r += [iface]
        return r
