# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Brocade.IronWare.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
import string
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Brocade.IronWare.get_interfaces"
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^(?P<interface>.+?)\s+is\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)",
        re.MULTILINE | re.IGNORECASE)
    rx_int_alias = re.compile(
        r"^(Description|Vlan alias name is)\s*(?P<alias>.*?)$",
        re.MULTILINE | re.IGNORECASE)
    rx_int_mac = re.compile(r"address\s+is\s+(?P<mac>\S+)",
                            re.MULTILINE | re.IGNORECASE)
    rx_int_ipv4 = re.compile(r"Internet address is (?P<address>[0-9\.\/]+)",
                             re.MULTILINE | re.IGNORECASE)
    rx_vlan_list = re.compile(
        r"untagged|(?P<from>\w+\s[0-9\.\/]+)(?P<to>\sto\s[0-9\.\/]+)?",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        rip=[]
        try:
            c=self.cli("show ip rip int | inc ^Interface")
        except self.CLISyntaxError:
            c=""
        c=c.strip("\n")
        for ii in c.split("\n"):
            ii=ii.lower()
            if ii.find("ve")>0:
                ii=ii.replace("ve ","ve")
            else:
                ii=ii.replace("Eth ","")
            if ii !='':
                ii=ii.split(" ")[1]
            rip+=[ii]
        ospf=[]
        try:
            c=self.cli("sh ip ospf int | inc OSPF enabled")
        except self.CLISyntaxError:
            c=""
        c=c.strip("\n")
        for ii in c.split("\n"):
            ii=ii.lower().split(",")[0]
            if ii.startswith("ve "):
                ii=ii.replace("ve ","ve")
            elif ii.startswith("v"):
                ii=ii.replace("v","ve")
            elif ii.startswith("loop"):
                ii=ii.replace("loopback ","lb")
            elif ii.startswith("lb"):
                ii=ii
            elif ii != '':
                ii=ii.split(" ")[1]
            ospf+=[ii.strip()]
        pim=[]
        try:
            c=self.cli("sh ip pim int | inc ^Int")
        except self.CLISyntaxError:
            c=""
        if c!='':
            for ii in c.split("\n"):
                ii=ii.split(" ")[1]
                if ii.startswith("v"):
                    ii=ii.replace("v","ve")
                else:
                    ii=ii.replace("e","")
                pim+=[ii]
        dvmrp=[]
        try:
            c=self.cli("sh ip dvmrp int | inc ^Int")
        except self.CLISyntaxError:
            c=""
        if c!='':
            c=c.strip("\n")
            for ii in c.split("\n"):
                ii= ii.split(" ")[1]
                if ii.startswith("v"):
                    ii=ii.replace("v","ve")
                else:
                    ii=ii.replace("e","")
                dvmrp+=[ii]
        stp=[]
        try:
            c=self.cli("show span | inc /")
        except self.CLISyntaxError:
            c=""
        c=c.strip("\n")
        for ii in c.split("\n"):
            ii=ii.split(" ")[0]
        gvrp=[]
        try:
            c=self.cli("show gvrp")
        except self.CLISyntaxError:
            c=""
        igmp=[]
        try:
            c=self.cli("sh ip igmp int | exc group:")
        except self.CLISyntaxError:
            c=""
        c=c.strip("\n")
        for ii in c.split("\n"):
            ii=ii.strip()
            ii=ii.split(" ")[0]
            ii=ii.strip(":")
            if ii.startswith("v"):
                ii=ii.replace("v","ve")
            else:
                ii=ii.replace("e","")
            igmp+=[ii]
        interfaces=[]
        shrunvlan = self.cli("sh running-config vlan")
        tagged = {}
        untagged = {}
        r = []
        for v in shrunvlan.split('!'):
            match = self.rx_vlan_list.findall(v)
            if match:
                tag = 1
                m2 = match
                for m in match:
                    if not m[0]:
                        tag = 0
                        continue

                    if m[0].split()[0] == "vlan":
                        vlan = int(m[0].split()[1])
                        continue

                    elif m[0][:3] == "ve ":
                        ifc = ''.join(m[0].split())
                        if ifc in untagged:
                            untagged[ifc].append(vlan)
                        else:
                            untagged[ifc] = vlan
                        continue

                    elif not m[0].split()[0] == 'ethe':
                        continue

                    elif not m[1]:
                        ifc = m[0].split()[1]
                        if tag == 1:
                            if ifc in tagged:
                                tagged[ifc].append(vlan)
                            else:
                                tagged[ifc] = [vlan]
                        else:
                            untagged[ifc] = vlan

                    else:
                        first = m[0].split()[1].split('/')[1]
                        last = m[1].split()[1].split('/')[1]
                        for n in range(int(first), int(last) + 1):
                            ifc = m[0].split()[1].split('/')[0] + '/' + repr(n)
                            if tag == 1:
                                if ifc in tagged:
                                    tagged[ifc].append(vlan)
                                else:
                                    tagged[ifc] = [vlan]
                            else:
                                untagged[ifc] = vlan

        c=self.cli("sh int br | excl Port")
        c=c.strip("\n")
        for ii in c.split("\n"):
            ii=ii.lower()
            ii=ii.replace("disabled"," disabled ")
            ii=ii.replace("disabn"," disabled n")
            ii=ii.replace("up"," up ")
            ii=ii.replace("  "," ")
            port=ii.split()
            if len(port)>1:
                ifname=port[0]
                if ifname.find("/")>0:
                    ift="physical"
                if ifname.find("e")>0:
                    ift="SVI"
                if ifname.find("b")>0:
                    ift="loopback"
                if ifname.find("m")>0:
                    ift="management"
                i = {
                    "name": ifname,
                    "type": ift,
                    "admin_status": port[1]=="up",
                    "oper_status": port[1]=="up",
                    "enabled_protocols": [],
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": port[1]=="up",
                        "oper_status": port[1]=="up"
                    }]
                }
                if ift=="SVI":
                    i['subinterfaces'][0].update({"vlan_ids":[untagged[ifname]]})
                    ipa=self.cli("show run int %s | inc ip addr" % ifname)
                    ipa=ipa.strip()
                    if len(ipa)>1:
                        i['subinterfaces'][0].update({"enabled_afi":["IPv4"]})
                        self.logger.debug("ip.split len:" + str(len(ipa.split())))
                        if len(ipa.split())>3:
                            ip_address="%s/%s" % (ipa.split()[2],IPv4.netmask_to_len(ipa.split()[3]))
                        else:
                            ip_address=ipa.split()[2]
                        i['subinterfaces'][0].update({"ipv4_addresses":[ip_address]})

                if len(port)>9:
                    desc=port[9]
                else:
                    desc=''
                i['subinterfaces'][0].update({"description":desc})
                if ift=="physical":
                    i['subinterfaces'][0].update({"is_bridge": True})
                    if ifname in tagged:
                        i['subinterfaces'][0].update({"tagged_vlans": tagged[ifname]})
                    if ifname in untagged:
                        i['subinterfaces'][0].update({"untagged_vlan": untagged[ifname]})
                l2protos=[]
                l3protos=[]
                if ifname in stp: l2protos+=["STP"]
                if ifname in gvrp: l2protos+=["GVRP"]
                i.update({"enabled_protocols": l2protos})
                # L3 protocols check:
                if ifname in rip: l3protos+=["RIP"]
                if ifname in ospf: l3protos+=["OSPF"]
                if ifname in pim: l3protos+=["PIM"]
                if ifname in dvmrp: l3protos+=["DVMRP"]
                if ifname in igmp: l3protos+=["IGMP"]
                i['subinterfaces'][0].update({"enabled_protocols":l3protos})

                interfaces+=[i]
        return [{"interfaces": interfaces}]
