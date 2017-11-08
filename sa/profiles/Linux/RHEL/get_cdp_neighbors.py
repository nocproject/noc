# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.RHEL.get_cdp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
### CDP demon ####

1) "ladvd"

see http://www.blinkenlights.nl/software/ladvd/

get ftp://ftp5.gwdg.de/pub/opensuse/repositories/home:/sten-blinkenlights/

# usermod -G ladvd -a <noc_username_for_this_host>


2) "llpdp"

see http://vincentbernat.github.com/lldpd/

get http://software.opensuse.org/download.html?project=home:vbernat&package=lldpd

usermod -G _lldpd -a <noc_user_for_this_username>

enable CDP in /etc/sysconfig/lldpd : LLDPD_OPTIONS="-c"

### KVM host ####

need drop CDP traffic  ethX -- bridge -- vnetX
dump CDP traffic
# tcpdump -nn -v -i bond0 -s 1500 -c 100 'ether[20:2] == 0x2000'

# iptables -I FORWARD -m mac --mac 01:00:0C:CC:CC:CC -j DROP


"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcdpneighbors import IGetCDPNeighbors


class Script(BaseScript):
    name = "Linux.RHEL.get_cdp_neighbors"
    interface = IGetCDPNeighbors
    """
    $ ladvdc -C -v
    Capability Codes:
	r - Repeater, B - Bridge, H - Host, R - Router, S - Switch,
	    W - WLAN Access Point, C - DOCSIS Device, T - Telephone, O - Other
	    
	    Device ID                      Local Intf    Proto   Hold-time    Capability    Port ID
	    gsw2-73-sar                    enp2s0        CDP     127          S             Gi1/0/4
	    example.ru                    eth0          CDP     115          HRS           vnet0
    """
    rx_ladvdc = re.compile(r"(?P<device_id>\S+)\s+(?P<local_interface>\S+)\s+"
                           r"CDP\s+\d+\s+\S+\s+(?P<remote_interface>\S+)\s+\n",
                           re.MULTILINE | re.DOTALL | re.IGNORECASE)

    """
    $ lldpcli show neighbors summary
    -------------------------------------------------------------------------------
    LLDP neighbors:
    -------------------------------------------------------------------------------
    Interface:    enp2s0, via: CDPv2
      Chassis:     
        ChassisID:    local gsw2-73-sar
        SysName:      gsw2-73-sar
      Port:        
        PortID:       ifname GigabitEthernet1/0/4
        PortDescr:    GigabitEthernet1/0/4
    ------------------------------------------------------------------------------- 
    
    """

    rx_lldpd = re.compile(r"Interface:\s+(?P<local_interface>\S+), via: CDPv2\n"
                          r"\s+Chassis:\s+\n"
                          r"\s+ChassisID:\s+\S+\s(?P<device_id>\S+)\n"
                          r"\s+SysName:\s+\S+\n"
                          r"\s+Port:\s+\n"
                          r"\s+PortID:\s+ifname (?P<remote_interface>\S+)\n"
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

        map = {"INTERFACE": "local_interface",
               "HOSTNAME": "device_id",
               "PORTNAME": "remote_interface"
               }
        # try ladvdc
        id_last = 999
        v = self.cli("ladvdc -b -C")
        # print "Status: ", v

        if "INTERFACE" in v:
            for l in v.splitlines():
                name, value = l.split('=')
                # print name, value
                id = int(name.split('_')[-1])
                # print id

                name2 = ''.join(name.split('_')[:-1])
                # print name2
                if name2 not in map:
                    continue

                if id != id_last:
                    neighbors += [{map[name2]: value.strip("'")}]
                    #   print value.strip("'")
                else:
                    if map[name2] == 'remote_interface':
                        neighbors[id][map[name2]] = self.profile.convert_interface_name_cisco(value.strip("'"))
                        #       print map[name2]
                    else:
                        neighbors[id][map[name2]] = value.strip("'")
                        #      print map[name2], value.strip("'")

                id_last = id

            return {
                "device_id": device_id,
                "neighbors": neighbors
            }

        """
        
        # Regexp block
        for match in self.rx_ladvdc.finditer(self.cli("ladvdc -C")):
            # ladvdc show remote CISCO(!!!) interface ->  "Gi1/0/4"
            # but cisco.iso profile need remote interface -> "Gi 1/0/4" !!!
            # check and convert remote_interface if remote host CISCO  
            if re.match(check_ifcfg, match.group("remote_interface")):
                remote_if = match.group("remote_interface")
            else:
                remote_if = self.profile.convert_interface_name_cisco(match.group("remote_interface"))

            neighbors += [{
                "device_id": match.group("device_id"),
                "local_interface": match.group("local_interface"),
                "remote_interface": remote_if,
            }]
        """
        # try lldpd
        for match in self.rx_lldpd.finditer(self.cli("lldpcli show neighbors summary")):
            if re.match(check_ifcfg, match.group("remote_interface")):
                remote_if = match.group("remote_interface")
            else:
                remote_if = self.profile.convert_interface_name_cisco(match.group("remote_interface"))

            neighbors += [{
                "device_id": match.group("device_id"),
                "local_interface": match.group("local_interface"),
                "remote_interface": remote_if,
            }]

        return {
            "device_id": device_id,
            "neighbors": neighbors
        }
