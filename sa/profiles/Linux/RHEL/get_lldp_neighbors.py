# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linux.RHEL.get_lldp_neighbors
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
#### LLDP demon ####

1) "ladvd"

see http://www.blinkenlights.nl/software/ladvd/

get ftp://ftp5.gwdg.de/pub/opensuse/repositories/home:/sten-blinkenlights/

# usermod -G ladvd -a <noc_username_for_this_host>


2) "llpdp"

see http://vincentbernat.github.com/lldpd/

get http://software.opensuse.org/download.html?project=home:vbernat&package=lldpd

usermod -G _lldpd -a <noc_user_for_this_username>

enable CDP in /etc/sysconfig/lldpd : LLDPD_OPTIONS="-c"

#### KVM host ####

dump CDP traffic 
# tcpdump -nn -v -i bond0 -s 1500 -c 100 'ether[20:2] == 0x2000'

# iptables -I FORWARD -m mac --mac 01:00:0C:CC:CC:CC -j DROP


"""
# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "Linux.RHEL.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    """
    $ ladvdc -C -v
    Capability Codes:
	r - Repeater, B - Bridge, H - Host, R - Router, S - Switch,
	    W - WLAN Access Point, C - DOCSIS Device, T - Telephone, O - Other
	    
	    Device ID                      Local Intf    Proto   Hold-time    Capability    Port ID
	    gsw2-73-sar                    enp2s0        LLDP     127          S             Gi1/0/4
	    example.ru                    eth0          LLDP     115          HRS           vnet0
    """
    rx_ladvdc = re.compile(r"(?P<device_id>\S+)\s+(?P<local_interface>\S+)\s+LLDP\s+\d+\s+\S+\s+(?P<remote_interface>\S+)\s+\n", re.MULTILINE | re.DOTALL | re.IGNORECASE)
    
    """
    $ lldpcli show neighbors summary
    -------------------------------------------------------------------------------
    LLDP neighbors:
    -------------------------------------------------------------------------------
    Interface:    eth0, via: LLDP
       Chassis:     
         ChassisID:    mac 00:21:5a:5d:3f:e4
         SysName:      vesta.san.ru
       Port:        
         PortID:       mac fe:54:00:75:b1:f5
         PortDescr:    vnet11
    ------------------------------------------------------------------------------- 
    
    """
    
    rx_lldpd = re.compile(r"Interface:\s+(?P<local_interface>\S+), via: LLDP\n"
                          r"\s+Chassis:\s+\n"
                          r"\s+ChassisID:\s+mac\s+(?P<remote_id>\S+)\n"
                          r"\s+SysName:\s+(?P<remote_system_name>\S+)\n"
                          r"\s+Port:\s+\n"
                          r"\s+PortID:\s+mac\s+(?P<remote_chassis_id>\S+)\n"
                          r"\s+PortDescr:\s+(?P<remote_port>\S+)\n"
                          , re.MULTILINE | re.DOTALL | re.IGNORECASE)
    
    def execute(self):
        """
        https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/
        """
        # Linux interface regex
        check_ifcfg = re.compile(r"(bond\d+|eno\d+|ens\d+|enp\d+s\d+|en[0-9a-fA-F]{8}|eth\d+|vnet\d+)",
                                 re.MULTILINE | re.DOTALL | re.IGNORECASE)

        device_id = self.scripts.get_fqdn()
        # Get neighbors
        neighbors = []
                
        # try ladvdc
        for match in self.rx_ladvdc.finditer(self.cli("ladvdc -L")):
            # ladvdc show remote CISCO(!!!) interface ->  "Gi1/0/4"
            # but cisco.iso profile need remote interface -> "Gi 1/0/4" !!!
            # check and convert remote_interface if remote host CISCO  
            if re.match(check_ifcfg, match.group("remote_interface")):
                remote_if = match.group("remote_interface")
            else:
                remote_if = self.profile.convert_interface_name_cisco(match.group("remote_interface"))

            neighbors += [{
                # "device_id": match.group("device_id"),
                "local_interface": match.group("local_interface"),
                # "remote_interface": remote_if,
            }]
        
        # try lldpd
        r = []
        for match in self.rx_lldpd.finditer(self.cli("lldpcli show neighbors summary")):
            if re.match(check_ifcfg, match.group("remote_port")):
                remote_if = match.group("remote_port")
            else:
                remote_if = self.profile.convert_interface_name_cisco(match.group("remote_port"))
            
            i = {"local_interface": match.group("local_interface"),
                 "neighbors": []
                 }
            
            # print (match.group("remote_port"))

            n = {
                'remote_capabilities': 4,
                "remote_chassis_id": match.group("remote_id"),
                'remote_chassis_id_subtype': 4,
                "remote_port": match.group("remote_chassis_id"),
                "remote_port_subtype": 3,
                "remote_system_name": match.group("remote_system_name"),
            }
            
            i["neighbors"] += [n]
            r += [i]

        return r
