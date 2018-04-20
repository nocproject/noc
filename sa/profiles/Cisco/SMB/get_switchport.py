# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Cisco.SMB.get_switchport
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
from noc.lib.validators import is_int


class Script(BaseScript):
    name = "Cisco.SMB.get_switchport"
    cache = True
    interface = IGetSwitchport

    rx_body = re.compile(
        r"^Port : .+"
        r"Port Mode: (?P<amode>\S+).+"
        r".+NATIVE[^\d]+(?P<nvlan>\d+).+",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_body2 = re.compile(
        r"Name: .+\n"
        r"Switchport: enable\n"
        r"Administrative Mode: (?P<amode>\S+).*\n"
        r"Operational Mode: .+\n"
        r"Access Mode VLAN: (?P<avlan>\S+)\s*\n"
        r"Access Multicast TV VLAN: .+\n"
        r"Trunking Native Mode VLAN: (?P<nvlan>\d+)",
        re.MULTILINE)
    rx_portmembers = re.compile(
        r"^\s*(?P<vid>\d+)\s+\S+\s+(?P<erule>\S+)\s+(?P<mtype>\S+)")
    rx_trunking = re.compile(
        r"Trunking VLANs: (?P<vlans>.+?)( \(Inactive\))?\s*\n"
        r"General PVID:", re.MULTILINE | re.DOTALL)

=======
##----------------------------------------------------------------------
## Cisco.SMB.get_switchport
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
    name = "Cisco.SMB.get_switchport"
    cache = True
    implements = [IGetSwitchport]

    rx_body = re.compile(r"^Port : .+"
                         r"Port Mode: (?P<amode>\S+).+"
                         r".+NATIVE[^\d]+(?P<nvlan>\d+).+",
                         re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_portmembers = re.compile(r"^\s*(?P<vid>\d+)\s+\S+\s+(?P<erule>\S+)\s+(?P<mtype>\S+)")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_descr_if = re.compile(r"^(?P<interface>\S+)\s*(?P<description>\S+)?")

    def get_description(self):
        r = []
        s = self.cli("show interfaces description", cached=True)
<<<<<<< HEAD
        for ll in s.split("\n"):
            match = self.rx_descr_if.match(ll.strip())
            if not match:
                continue
            else:
                interface = match.group("interface")
                if interface in ("Port", "Ch", "-------"):
                    continue
            r += [{
                "interface": self.profile.convert_interface_name(interface),
                "description": match.group("description")
=======
        for l in s.split("\n"):
            match = self.rx_descr_if.match(l.strip())
            if not match: continue
            else:
                interface = match.group("interface")
                if interface in ("Port", "Ch", "-------"): continue
                try: description = match.group("description")
                except: description = None
            r += [{
                "interface": self.profile.convert_interface_name(interface),
                "description": description
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            }]
        return r

    def execute(self):
        # Get portchannel members
        portchannels = {}  # portchannel name -> [members]
<<<<<<< HEAD
        for p in self.scripts.get_portchannel():
            portchannels[p["interface"]] = p["members"]
=======
        for p in self.scripts.get_portchannel(): portchannels[p["interface"]] = p["members"]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        # Get descriptions
        descriptions = {}  # interface name -> description
        interfaces = {}   # interface name -> status (True - up, False - down)
        # Prepare interface statuses
        for p in self.get_description():
            descriptions[p["interface"]] = p["description"]
<<<<<<< HEAD
            interfaces[p["interface"]] = False  # default is down
        for po in portchannels.keys():
            interfaces[po] = False
        if not interfaces:
            return []
=======
            interfaces[p["interface"]] = False # default is down
        for po in portchannels.keys(): interfaces[po] = False
        if not interfaces: return []
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        # Get vlans, as set([1,2,3,10])
        known_vlans = set([vlan["vlan_id"] for vlan in self.scripts.get_vlans()])

        # Set up interface statuses
        for intstatus in self.scripts.get_interface_status():
            if intstatus['interface'] in interfaces.keys():
                interfaces[intstatus['interface']] = intstatus['status']

<<<<<<< HEAD
        r = []  # reply
        # For each interface
        for interface in interfaces.keys():
            try:
                v = self.cli("show interfaces switchport %s" % interface)
            except self.CLISyntaxError:
                continue
=======
        r = []                  # reply
        # For each interface
        for interface in interfaces.keys():
            v = self.cli("show interfaces switchport %s" % interface)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            is_trunk = None
            is_qnq = None
            untagged = None
            tagged = []

            # Parse header
<<<<<<< HEAD
            match = self.rx_body.search(v)
            if not match:
                match = self.rx_body2.search(v)
            amode = match.group("amode").strip().lower()
            # can native vlan mismatch with untagged?
            untagged = match.group("nvlan")
=======
            match = self.re_search(self.rx_body, v)
            amode = match.group("amode").strip().lower()
            untagged = int(match.group("nvlan")) # can native vlan mismatch with untagged?
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            if amode in ("trunk", "general"):
                is_trunk = True
                is_qnq = False
            elif amode in ("access"):
<<<<<<< HEAD
                if "avlan" in match.groups():
                    untagged = match.group("avlan")
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                is_trunk = False
                is_qnq = False
            elif amode in ("customer"):
                is_qnq = True
                is_trunk = True

<<<<<<< HEAD
            if is_trunk:
                match = self.rx_trunking.search(v)
                if match:
                    vlans = match.group("vlans").replace("\n", ",")
                    tagged = self.expand_rangelist(vlans)
                else:
                    # Parse list of vlans
                    for ll in v.split("\n"):
                        match = self.rx_portmembers.match(ll.strip())
                        if match:
                            vid = int(match.group("vid"))
                            erule = match.group("erule").lower()
                            if erule in ("tagged"):
                                tagged.append(vid)
=======
            # Parse list of vlans
            for l in v.split("\n"):
                match = self.rx_portmembers.match(l.strip())
                if match:
                    vid = int(match.group("vid"))
                    erule = match.group("erule").lower()
                    if erule in ("tagged"):
                        tagged.append(vid)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

            iface = {
                "interface": interface,
                "status": interfaces[interface],
<<<<<<< HEAD
                "tagged": [vl for vl in tagged if vl in known_vlans],
=======
                "tagged": [v for v in tagged if v in known_vlans],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                "members": portchannels.get(interface, []),
                "802.1Q Enabled": is_trunk,
                "802.1ad Tunnel": is_qnq,
            }
<<<<<<< HEAD
            if is_int(untagged):
=======
            if untagged:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                iface["untagged"] = untagged
            if interface in descriptions.keys():
                if descriptions[interface]:
                    iface["description"] = descriptions[interface]

            r += [iface]
        return r
