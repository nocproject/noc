# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
import re
import binascii

rx_localport=re.compile(r"^\s*Eth(.+?)\s*\| MAC Address\s+(\S+).+?$",re.MULTILINE|re.DOTALL)
rx_neigh=re.compile(r"(?P<local_if>Eth\s\S+)\s+\|\s+(?P<id>\S+).*?(?P<name>\S+)$",re.MULTILINE|re.IGNORECASE)
rx_detail=re.compile(r".*Chassis Id\s+:\s(?P<id>\S+).*?PortID Type\s+:\s(?P<p_type>[^\n]+).*?PortID\s+:\s(?P<p_id>[^\n]+).*?SysName\s+:\s(?P<name>\S+).*?SystemCapSupported\s+:\s(?P<capability>[^\n]+).*",re.MULTILINE|re.IGNORECASE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES35xx.get_lldp_neighbors"
    implements=[IGetLLDPNeighbors]
    def execute(self):
        ifs=[]
        r=[]
        # EdgeCore ES3526 advertises MAC address(3) port sub-type, so local_interface_id parameter required
        # Collect data
        local_port_ids={} # name -> id
        for port,local_id in rx_localport.findall(self.cli("show lldp info local-device")):
            local_port_ids["Eth "+port]=MACAddressParameter().clean(local_id)
        
        v=self.cli("show lldp info remote-device")
        for l in v.splitlines():
            l=l.strip()
            match=rx_neigh.match(l)
            if match:
                ifs.append({
                    "local_interface" : match.group("local_if"),
                    "neighbors"       : [],
                })
                
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"]=local_port_ids[i["local_interface"]]
            v=self.cli("show lldp info remote detail %s"%i["local_interface"])
            match=rx_detail.search(v)
            n={"remote_chassis_id_subtype":4}
            if match:
                n["remote_port_subtype"]={"MAC Address" : 3, "Interface name" : 5, "Inerface alias" : 5, "Local" : 7}[match.group("p_type")]
                if n["remote_port_subtype"]==3:
                    remote_port=MACAddressParameter().clean(match.group("p_id"))
                else:
                    # Removing bug
                    remote_port=binascii.unhexlify(''.join(match.group("p_id").split('-')))
                    remote_port=remote_port.rstrip('\x00')
                n["remote_chassis_id"]=match.group("id")
                n["remote_system_name"]=match.group("name")
                n["remote_port"]=remote_port
                # Get capability
                cap=0
                for c in match.group("capability").strip().split(", "):
                        cap|={
                        "Other" : 1, "Repeater" : 2, "Bridge" : 4,
                        "WLAN" : 8, "Router" : 16, "Telephone" : 32,
                        "Cable" : 64, "Station" : 128
                        }[c]
                n["remote_capabilities"]=cap
            i["neighbors"]+=[n]
            r+=[i]
        return r
