# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaces
##
## Juniper.JUNOS.get_interfaces
##
## @todo: virtual routers
## @todo: vrfs
## @todo: vlan ids of the units
class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_interfaces"
    implements=[IGetInterfaces]
    
    rx_phy_split=re.compile(r"^Physical interface:\s+", re.MULTILINE)
    rx_phy_name=re.compile(r"^(?P<ifname>\S+), (?P<admin>Enabled|Disabled), Physical link is (?P<oper>Up|Down)", re.MULTILINE|re.IGNORECASE)
    rx_phy_description=re.compile(r"^\s+Description:\s+(?P<description>.+?)\s*$", re.MULTILINE)
    rx_phy_ifindex=re.compile(r"SNMP ifIndex: (?P<ifindex>\d+)", re.MULTILINE|re.IGNORECASE)
    rx_phy_mac=re.compile(r"^\s+Current address: (?P<mac>\S+),", re.MULTILINE)
    
    rx_log_split=re.compile(r"^\s+Logical interface\s+", re.MULTILINE)
    rx_log_name=re.compile(r"^(?P<name>\S+).+?SNMP ifIndex (?P<ifindex>\d+)", re.IGNORECASE)
    rx_log_protocol=re.compile(r"^\s+Protocol\s+", re.MULTILINE)
    rx_log_pname=re.compile(r"^(?P<proto>\S+?),")
    rx_log_address=re.compile(r"^\s+Local:\s+(?P<address>\S+)", re.MULTILINE)
    rx_log_netaddress=re.compile(r"^\s+Destination: (?P<dest>\S+?),\s+Local: (?P<local>\S+?),", re.MULTILINE)
    rx_log_ae=re.compile(r"AE bundle: (?P<bundle>\S+?)\.\d+", re.MULTILINE)
    
    internal_interfaces=re.compile(r"^(lc-|cbp|demux|dsc|em|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip)")
    internal_interfaces_olive = re.compile(r"^(lc-|cbp|demux|dsc|gre|ipip|lsi|mtun|pimd|pime|pp|tap|pip)")
    def execute(self):
        interfaces=[]
        version = self.scripts.get_version()
        if version["platform"] == "olive":
            internal = self.internal_interfaces_olive
        else:
            internal = self.internal_interfaces
        v=self.cli("show interfaces")
        for I in self.rx_phy_split.split(v)[1:]:
            L=self.rx_log_split.split(I)
            phy=L.pop(0)
            match=self.re_search(self.rx_phy_name, phy)
            name=match.group("ifname")
            # Skip internal interfaces
            if internal.search(name):
                continue
            # Detect interface type
            if name.startswith("lo"):
                iftype="loopback"
            elif name.startswith("fxp"):
                iftype="management"
            elif name.startswith("ae"):
                iftype="aggregated"
            else:
                iftype="physical"
            # Get interface parameters
            iface={
                "name"         : name,
                "admin_status" : match.group("admin").lower()=="enabled",
                "oper_status"  : match.group("oper").lower()=="up",
                "type"         : iftype,
            }
            # Get description
            match=self.rx_phy_description.search(phy)
            if match:
                iface["description"]=match.group("description")
            # Get MAC
            match=self.rx_phy_mac.search(phy)
            if match:
                iface["mac"]=match.group("mac")
            # Process subinterfaeces
            subs=[]
            for s in L:
                match=self.re_search(self.rx_log_name, s)
                sname=match.group("name")
                if sname.startswith("lo0.163"):
                    continue
                si={
                    "name"        : sname,
                    "snmp_ifindex": match.group("ifindex"),
                    "admin_status": True,
                    "oper_status" : True,
                    #"description"    : StringParameter(required=False),
                    #"mac"            : MACAddressParameter(required=False),
                    
                }
                # Get description
                match=self.rx_phy_description.search(s)
                if match:
                    si["description"]=match.group("description")
                # Process protocols
                ipv4=[]
                iso=[]
                for p in self.rx_log_protocol.split(s)[1:]:
                    match=self.re_search(self.rx_log_pname, p)
                    proto=match.group("proto")
                    local_addresses=self.rx_log_address.findall(p)
                    if proto=="iso":
                        # Protocol ISO
                        si["is_iso"]=True
                        if local_addresses:
                            si["iso_addresses"]=local_addresses
                    elif proto=="inet":
                        # Protocol IPv4
                        si["is_ipv4"]=True
                        si["ipv4_addresses"]=["%s/32"%a for a in local_addresses]
                        # Find connected networks
                        for match in self.rx_log_netaddress.finditer(p):
                            net,addr=match.groups()
                            n,m=net.split("/")
                            si["ipv4_addresses"]+=["%s/%s"%(addr,m)]
                    elif proto=="aenet":
                        # Aggregated
                        match=self.re_search(self.rx_log_ae, p)
                        bundle=match.group("bundle")
                        iface["aggregated_interface"]=bundle
                # Append to subinterfaces list
                subs+=[si]
            # Append to collected interfaces
            iface["subinterfaces"]=subs
            interfaces+=[iface]
        return [{
            "forwarding_instance" : "default",
            "type"                : "ip",
            "interfaces"          : interfaces,
        }]
    
