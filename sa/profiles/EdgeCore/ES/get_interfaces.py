# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_interfaces
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces, InterfaceTypeError, MACAddressParameter

class Script(NOCScript):
    name = "EdgeCore.ES.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 240
    cache = True
    types = {
        "Eth": "physical",
        "Trunk": "aggregated",
        "VLAN": "SVI"
    }


    rx_ip_if_35 = re.compile(r".*?IP Address and Netmask:\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+(?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+on\s+(?P<name>[^\n]+?),\n",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_svi_name_stat_4612 = re.compile(r"(?P<name>Vlan[^\n]+?)\s+is\s+(?P<stat>up|down)",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_ip_if_4612 = re.compile(r".*?Interface address is\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}),\s+mask is\s+(?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_svi_name_stat_3510MA =  re.compile(r"(?P<name>Vlan[^\n]+?)\s+is Administrative\s+(?P<a_stat>Up|Down)\s+-\s+Link\s+(?P<o_stat>Up|Down)",
                                     re.MULTILINE | re.IGNORECASE | re.DOTALL)

    rx_ip_if_3510MA = re.compile(r".*?IP address:\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+Mask:\s+(?P<mask>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
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
        descr_ = {}
        stat_ = {}
        tagged_ = {}
        untagged_ = {}
        end_if = False

        # Tested only ES3510MA, ES3510, ES3526XAv2, ES3528M, ES3552M, ES4612
        if (self.match_version(platform__contains="4626")):
                raise self.NotSupportedError()
        
        # Get interface status
        for p in self.scripts.get_interface_status():
            intf = p["interface"]
            name_[intf] = intf
            mac_[intf] = p["mac"]
            if "description" in p:
                descr_[intf] = p["description"]
            stat_[intf] = p["status"]

        # Get switchport's
        for p in self.scripts.get_switchport():
            intf = p["interface"]
            if "tagged" in p:
                tagged_[intf] = p["tagged"]
            if "untagged" in p:
                untagged_[intf] = p["untagged"]
        

        # Get SVI interfaces on 4612
        if (self.match_version(platform__contains="4612")):
            for ls in self.cli("show ip interface").splitlines():
                match = self.rx_svi_name_stat_4612.search(ls)
                if match:
                    ip_addr = []
                    sub = {}
                    namesviif = match.group("name").upper()
                    stat = match.group("stat")
                   
                match = self.rx_ip_if_4612.search(ls)
                if match:
                    ip = match.group("ip")
                    mask = match.group("mask")
                    ip_addr += [IPv4(ip, netmask = mask).prefix]

                if (ls.strip().startswith("Split")):
                    if not ip_addr:
                        continue
                    type = "SVI"
                    vlan_ids = [int(namesviif[5:])]
                    mac_svi = mac_[namesviif]
                    sub = {
                       "name": namesviif,
                       "admin_status": stat == "up",
                       "oper_status": stat == "up",
                       "is_ipv4": True,
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


        # Dirty-hack 3510/3526/3528/3552 managment SVI interface
        if (self.match_version(platform__contains="3510") or 
            self.match_version(platform__contains="3526") or
            self.match_version(platform__contains="3528") or
            self.match_version(platform__contains="3552")):
       
           # Dirty-hack 3510MA managment SVI interface
           if (self.match_version(platform__contains="3510MA")):
              for ls in self.cli("show ip interface").splitlines():
                  match = self.rx_svi_name_stat_3510MA.search(ls)
                  if match:
                     ip_addr = []
                     sub = {}
                     namesviif = match.group("name").upper()
                     a_stat = match.group("a_stat")
                     o_stat = match.group("o_stat")

                  match = self.rx_ip_if_3510MA.search(ls)
                  if match:
                     ip = match.group("ip")
                     mask = match.group("mask")
                     ip_addr = [IPv4(ip, netmask = mask).prefix]
                     type = "SVI"
                     vlan_ids = [int(namesviif[5:])]
                     if namesviif in mac_:
                         mac_svi = mac_[namesviif]
                     sub = {
                        "name": namesviif,
                        "admin_status": a_stat == "Up",
                        "oper_status": o_stat == "Up",
                        "is_ipv4": True,
                        "ipv4_addresses": ip_addr,
                        "vlan_ids": vlan_ids,
                     }
                     if mac_svi:
                       sub["mac"] = mac_svi
                     ifaces[namesviif] = {
                        "name": namesviif,
                        "admin_status": a_stat == "Up",
                        "oper_status": o_stat == "Up",
                        "type": type,
                        "subinterfaces": [sub],
                     }
                     if mac_svi:
                       ifaces[namesviif]["mac"] = mac_svi

           # 3510/3526/3528/3552
           for ls in self.cli("show ip interface").splitlines():
               match = self.rx_ip_if_35.search(ls + "\n")
               if match:
                   ip = match.group("ip")
                   mask = match.group("mask")
                   namesviif = match.group("name")
                   ip_addr = IPv4(ip, netmask = mask).prefix
                   status = "Up"
                   type = "SVI"
                   vlan_ids = [int(namesviif[5:])]
                   if namesviif in mac_:
                       mac_svi = mac_[namesviif]
                   sub = {
                       "name": namesviif,
                       "admin_status": status == "Up",
                       "oper_status": status == "Up",
                       "is_ipv4": True,
                       "ipv4_addresses": [ip_addr],
                       "vlan_ids": vlan_ids,
                   }
                   if mac_svi:
                       sub["mac"] = mac_svi
                   ifaces[namesviif] = {
                       "name": namesviif,
                       "admin_status": status == "Up",
                       "oper_status": status == "Up",
                       "type": type,
                       "subinterfaces": [sub],
                   }
                   if mac_svi:
                       ifaces[namesviif]["mac"] = mac_svi

        # Pre-process portchannel members
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            t = pc["type"] == "L"
            for m in pc["members"]:
                portchannel_members[m] = (i, t)


        # Simulate hard working
        
        # set name ifaces         
        for current in name_:
            is_svi = current.startswith("VLAN")
            if is_svi:
                continue
            ifaces[current] = {
               "name": current
            }
        # other
        for current in ifaces:
            is_svi = current.startswith("VLAN")
            if is_svi:
                continue 
            is_bundle = current.startswith("Trunk")
            if is_bundle:
                ifaces[current]["mac"] = mac_[current] 
                ifaces[current]["admin_status"] = stat_[current]
                ifaces[current]["oper_status"] = stat_[current]
                ifaces[current]["type"] = "aggregated"
                # Sub-interface
                sub = {
                   "name": current,
                   "admin_status": stat_[current],
                   "oper_status": stat_[current],
                   "is_bridge": True,
                   "tagged_vlans": tagged_[current],
                   "untagged_vlan": untagged_[current],
                   "mac": mac_[current],
                }
                if current in descr_:
                   ifaces[current]["description"] = descr_[current]
                   sub["description"] = descr_[current]
                ifaces[current]["subinterfaces"] = [sub]
                
            else:
                ifaces[current]["mac"] = mac_[current]
                ifaces[current]["admin_status"] = stat_[current]
                ifaces[current]["oper_status"] = stat_[current]
                ifaces[current]["type"] = "physical"
                sub = {
                   "name": current,
                   "admin_status": stat_[current],
                   "oper_status": stat_[current],
                   "is_bridge": True,
                   "mac": mac_[current],
                }

                if current in descr_:
                   ifaces[current]["description"] = descr_[current]
                   sub["description"] = descr_[current]
                ifaces[current]["subinterfaces"] = [sub]
                if current in tagged_:
                   sub["tagged_vlans"] = tagged_[current]
                if current in untagged_:
                   sub["untagged_vlan"] = untagged_[current] 


                # Portchannel member
                if current in portchannel_members:
                   ai, is_lacp = portchannel_members[current]
                   ifaces[current]["aggregated_interface"] = ai
                   ifaces[current]["is_lacp"] = is_lacp

            
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
