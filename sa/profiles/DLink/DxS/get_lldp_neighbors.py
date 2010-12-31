# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
""" 
""" 
##
##  This is a draft variant
##  I need to find some missing values
##

from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int,is_ipv4
import re

rx_line=re.compile(r"\s*Port ID :\s+",re.MULTILINE)
rx_id=re.compile(r"^(?P<port_id>\S+)",re.MULTILINE)
rx_re_ent=re.compile(r"Remote Entities Count\s+:\s+(?P<re_ent>\d+)",re.MULTILINE)
rx_line1=re.compile(r"\s*Entity\s+\d+")
rx_remote_chassis_id_subtype=re.compile(r"Chassis ID Subtype\s+: (?P<subtype>.+)",re.MULTILINE)
rx_remote_chassis_id=re.compile(r"Chassis ID\s+: (?P<id>\S+)",re.MULTILINE)
rx_remote_port_id_subtype=re.compile(r"Port ID Subtype\s+: (?P<subtype>\S+)",re.MULTILINE)
rx_remote_port_id=re.compile(r"Port ID\s+: (?P<port>.+)",re.MULTILINE)
rx_remote_system_name=re.compile(r"System Name\s+: (?P<name>.+)",re.MULTILINE)
rx_remote_capabilities=re.compile(r"System Capabilities\s+: (?P<capabilities>.+)",re.MULTILINE)

class Script(NOCScript):
    name="DLink.DxS.get_lldp_neighbors"
    implements=[IGetLLDPNeighbors]
    def execute(self):
        r=[]
        v=self.cli("show lldp remote_ports")
        # For each interface
        for s in rx_line.split(v)[1:]:
            match=rx_id.search(s)
            if not match:
                continue
            port_id = match.group("port_id")
            match=rx_re_ent.search(s)
            if not match:
                continue
            re_ent = int(match.group("re_ent"))
            if re_ent == 0:
                # Remote Entities Count : 0
                continue
            i={"local_interface":port_id, "neighbors":[]}
            # For each neighbor
            for s1 in rx_line1.split(s)[1:]:
                n={}
                # remote_chassis_id_subtype
                match=rx_remote_chassis_id_subtype.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_chassis_id_subtype\n\n\n\n\n"
                    continue
                remote_chassis_id_subtype = match.group("subtype").strip()
                # TODO: Find other subtypes
                if remote_chassis_id_subtype == "MAC Address":
                    n["remote_chassis_id_subtype"] = 4
                # remote_chassis_id
                match=rx_remote_chassis_id.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_chassis_id\n\n\n\n\n"
                    continue
                n["remote_chassis_id"] = match.group("id").strip()
                # remote_port_subtype
                match=rx_remote_port_id_subtype.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_port_id_subtype\n\n\n\n\n"
                    continue
                remote_port_subtype = match.group("subtype").strip()
                # TODO: Find other subtypes
                if remote_port_subtype == "Interface Name":
                    n["remote_port_subtype"] = 5
                elif remote_port_subtype == "Local":
                    n["remote_port_subtype"] = 7
                # remote_port
                match=rx_remote_port_id.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_port_id\n\n\n\n\n"
                    continue
                n["remote_port"] = match.group("port").strip()
                # remote_system_name
                match=rx_remote_system_name.search(s1)
                if match:
                    remote_system_name = match.group("name").strip()
                    if remote_system_name != "":
                        n["remote_system_name"] = remote_system_name
                # remote_capabilities
                match=rx_remote_capabilities.search(s1)
                if not match:
                    # Debug string
                    print "\n\n\n\n\nremote_capabilities\n\n\n\n\n"
                    continue
                remote_capabilities = match.group("capabilities").strip()
                caps = 0
                # TODO: Find other capabilities
                if remote_capabilities.find("Other") != -1:
                    caps += 1
                if remote_capabilities.find("Repeater") != -1:
                    caps += 2
                if remote_capabilities.find("Bridge") != -1:
                    caps += 4
                if remote_capabilities.find("WLAN Access Point") != -1:
                    caps += 8
                if remote_capabilities.find("Router") != -1:
                    caps += 16
                if remote_capabilities.find("Telephone") != -1:
                    caps += 32
                if remote_capabilities.find("DOCSIS Cable Device") != 1:
                    caps += 64
                if remote_capabilities.find("Station Only") != -1:
                    caps += 128
                n["remote_capabilities"] = caps
                i["neighbors"]+=[n]
            r+=[i]
        return r
