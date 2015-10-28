# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Opticin.OS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.lib.ip import IPv4
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces, InterfaceTypeError, MACAddressParameter

class Script(BaseScript):
    name = "Opticin.OS.get_interfaces"
    interface = IGetInterfaces

    cache = True

    rx_svi_name = re.compile(r"^system management vlan:\s+(?P<vl_id>\d)$",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_ip_if = re.compile(r"^System IP:\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_ip_mask = re.compile(r"^System Mask:\s+(?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(|\s+)$",                           
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_ip_mac = re.compile(r"System MAC[^:]*?:\s*(?P<mac>\S+)$",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    def execute(self):
        ifaces = {}
        current = None
        is_bundle = False
        is_svi = False
        vlan_ids = []
        mac_svi = ""        
        name_ = {}
        mac_ = {}
        snmp_ifindex_ = {}
        descr_ = {}
        stat_ = {}
        tagged_ = {}
        untagged_ = {}
        end_if = False

        # Get interface status
        for p in self.scripts.get_interface_status():
            intf = p["interface"]
            name_[intf] = intf
            if "mac" in p:
                mac_[intf] = p["mac"]
            if "description" in p:
                descr_[intf] = p["description"]
            stat_[intf] = p["status"]
            if "snmp_ifindex" in p:
                snmp_ifindex_[intf] = p["snmp_ifindex"]

        # Get switchport's
        for p in self.scripts.get_switchport():
            intf = p["interface"]
            if "tagged" in p:
                tagged_[intf] = p["tagged"]
            if "untagged" in p:
                untagged_[intf] = p["untagged"]

        # Get SVI interface
        ip_addr = []
        sub = {}
        for ls in self.cli("sh system").splitlines():
            match = self.rx_svi_name.search(ls)
            if match:
                namesviif = "Vlan " + match.group("vl_id").upper()
            match = self.rx_ip_if.search(ls)
            if match:
                ip = match.group("ip")
            match = self.rx_ip_mask.search(ls)
            if match:
                mask = match.group("mask")
                ip_addr += [IPv4(ip, netmask = mask).prefix]
            match = self.rx_ip_mac.search(ls)
            if match:
                mac_svi = MACAddressParameter().clean(match.group("mac"))             
        type = "SVI"
        stat = "up"
        vlan_ids = [int(namesviif[5:])]
        enabled_afi = ["IPv4"]
        sub = {
              "name": namesviif,
              "admin_status": stat == "up",
              "oper_status": stat == "up",
              "is_ipv4": True,
              "enabled_afi": enabled_afi,
              "ipv4_addresses": ip_addr,
              "vlan_ids": vlan_ids,
              "mac": mac_svi,
        }
        ifaces[namesviif] = {
              "name": namesviif,
              "admin_status": stat == "up",
              "oper_status": stat == "up",
              "type": type,
              "mac": mac_svi,
              "subinterfaces": [sub],
        }

        # set name ifaces         
        for current in name_:
            ifaces[current] = {
               "name": current
            }
        # other
        for current in ifaces:
            is_svi = current.startswith("Vlan")
            if is_svi:
                continue
            if current in mac_:
                ifaces[current]["mac"] = mac_[current]
            ifaces[current]["admin_status"] = stat_[current]
            ifaces[current]["oper_status"] = stat_[current]
            ifaces[current]["type"] = "physical"
            ifaces[current]["enabled_protocols"] = []
            enabled_afi = ["BRIDGE"]
            sub = {
               "name": current,
               "admin_status": stat_[current],
               "oper_status": stat_[current],
               "is_bridge": True,
               "enabled_afi": enabled_afi,
            }
            if current in mac_:
               sub["mac"] = mac_[current]
            if current in tagged_:
               sub["tagged_vlans"] = tagged_[current]
            if current in untagged_:
               sub["untagged_vlan"] = untagged_[current] 
            if current in snmp_ifindex_:
               sub["snmp_ifindex"] = snmp_ifindex_[current]
            ifaces[current]["subinterfaces"] = [sub]
            
        # Get VRFs and "default" VRF interfaces
        r = []
        seen = set()
        vpns = [{
            "name": "default",
            "type": "ip",
            "interfaces": []
            }]
        for fi in vpns:
            # Forwarding instance
            rr = {
                "forwarding_instance": fi["name"],
                "type": fi["type"],
                "interfaces": []
            }
            rd = fi.get("rd")
            if rd:
                rr["rd"] = rd
            # create ifaces
                
            rr["interfaces"] = ifaces.values()
        r += [rr]
        # Return result
        return r
