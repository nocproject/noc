# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
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
    name = "HP.ProCurve.get_switchport"
    cache = True
    implements = [IGetSwitchport]

    objstr = {"ifName": "interface",
              "ifDescr": "description",
              "ifOperStatus": "status"
              }

    def getVlanPort(self):

        untag = {}
        tag = {}
        egr = {}
        lmap = {"dot1qVlanStaticUntaggedPorts": untag,
                "dot1qVlanStaticEgressPorts": egr,
                }
        stat = 'dot1qVlanStatic'
        lines = self.cli("walkMIB " + " ".join(lmap.keys())).split(stat)[1:-1]

        for l in lines:
                    inc = 0
                    leaf, val = l.split(' = ')
                    type, vlan = leaf.split('.')
                    lmap[stat+type][int(vlan)] = []
                    for hex in val.split():
                        dec = int(hex, 16)
                        bit = 1
                        for p in range(8, 0, -1):
                            if dec & bit == bit:
                                lmap[stat+type][int(vlan)] += [p + inc]
                            bit <<= 1
                        inc = inc + 8

        for i in egr.keys():
            for j in egr[i]:
                if not j in untag[i]:
                    if not i in tag.keys():
                        tag[i] = []
                    tag[i] += [j]
        return untag, tag

    def execute(self):
        port = self.cli("walkMIB dot1dBaseNumPorts").split('=')[1]
        portsnum = int(re.sub(r'[^\d-]+', '', port))
        untagged, tagged = self.getVlanPort()
        iface = {}
        sports = []
        step = len(self.objstr)
        lines = self.cli("walkMIB " + " "
                         .join(self.objstr.keys())).split("\n")[:-1]
        portchannel_members = {}  # member -> (portchannel, type)
        portchannels = {}  # portchannel name -> [members]

        for p in self.scripts.get_portchannel():
            portchannels[p["interface"]] = p["members"]

        i = 0
        for s in range(len(lines) / step):

            if i == portsnum * step:
                break

            for strn in lines[i:i + step]:
                leaf = strn.split(".")[0]
                val = strn.split("=")[1].lstrip()
                if leaf[-6:] == "ifName":
                    iface[self.objstr[leaf]] = val
                elif leaf[-6:] == "Status":
                    iface[self.objstr[leaf]] = val == "1"
                elif leaf[-7:] == "ifDescr":
                    iface[self.objstr[leaf]] = val
            ifindex = int(strn.split('=')[0].split(".")[1])
            iface["untagged"] = 1
            for t in untagged.keys():
                if ifindex in untagged[t]:
                    iface["untagged"] = t
            iface["tagged"] = []
            for t in tagged.keys():
                if t == iface["untagged"]:
                    continue
                if ifindex in tagged[t]:
                    iface["tagged"] += [t]

            iface['members'] = portchannels.get(iface["interface"], [])
            if iface['tagged']:
                iface["802.1Q Enabled"] = True
            else:
                iface["802.1Q Enabled"] = False
            iface["802.1ad Tunnel"] = False

            sports += [iface]
            iface = {}

            i = i + step

        return sports
