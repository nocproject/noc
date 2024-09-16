# ---------------------------------------------------------------------
# OS.Linux.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
## LLDP demon ####

1) "ladvd"

see http://www.blinkenlights.nl/software/ladvd/

get ftp://ftp5.gwdg.de/pub/opensuse/repositories/home:/sten-blinkenlights/

# usermod -G ladvd -a <noc_username_for_this_host>


2) "llpdp"

see http://vincentbernat.github.com/lldpd/

get http://software.opensuse.org/download.html?project=home:vbernat&package=lldpd

usermod -G _lldpd -a <noc_user_for_this_username>

enable CDP in /etc/sysconfig/lldpd : LLDPD_OPTIONS="-c"

## KVM host ####

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
    name = "OS.Linux.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldpd = re.compile(
        r"Interface:\s+(?P<local_interface>\S+), via: LLDP\n"
        r"\s+Chassis:\s+\n"
        r"\s+ChassisID:\s+mac\s+(?P<remote_id>\S+)\n"
        r"\s+SysName:\s+(?P<remote_system_name>\S+)\n"
        r"\s+Port:\s+\n"
        r"\s+PortID:\s+(?P<remote_port_type>\S+)\s+(?P<remote_chassis_id>\S+)\n"
        r"\s+PortDescr:\s+(?P<remote_port>\S+)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    # Linux interface regex
    check_ifcfg = re.compile(
        r"(bond\d+|eno\d+|ens\d+|enp\d+s\d+|en[0-9a-fA-F]{8}|eth\d+|vnet\d+|vif\d+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )

    def execute(self):
        """
        https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/
        """

        # device_id = self.scripts.get_fqdn()

        # Get neighbors
        neighbors = []
        remotehost = {}

        # try ladvdc
        map = {
            "INTERFACE": "local_interface",
            "HOSTNAME": "remote_chassis_id",
            "PORTNAME": "remote_port",
            "CAPABILITIES": "remote_capabilities",
        }

        # try ladvdc
        id_last = 999
        v = self.cli("ladvdc -b -L")

        if "INTERFACE" in v:
            for line in v.splitlines():
                name, value = line.split("=")
                id = int(name.split("_")[-1])

                name2 = "".join(name.split("_")[:-1])
                if name2 not in map:
                    continue

                if id != id_last and map[name2] == "local_interface":
                    neighbors += [{map[name2]: value.strip("'"), "neighbors": [remotehost]}]
                elif map[name2] == "remote_capabilities":
                    remotehost.update({map[name2]: "30"})
                elif map[name2] == "remote_port":
                    # try convert to Cisco format
                    remotehost.update({"remote_port_subtype": 5})
                    remotehost.update({map[name2]: value.strip("'")})
                else:
                    remotehost.update({map[name2]: value.strip("'")})

                id_last = id

            return neighbors

        ##############
        # try lldpd

        r = []
        v = self.cli("lldpcli show neighbors summary")
        if "Permission denied" in v:
            self.logger.info(
                "Add <NOCuser> to _lldpd group. Like that ' "
                "# usermod -G _lldpd -a <NOCuser> . And restart lldpd daemon' "
            )
            return r

        else:
            for match in self.rx_lldpd.finditer(self.cli("lldpcli show neighbors summary")):
                if self.check_ifcfg.match(match.group("remote_port")):
                    remote_if = match.group("remote_port")
                else:
                    remote_if = self.profile.convert_interface_name_cisco(
                        match.group("remote_port")
                    )

                i = {"local_interface": match.group("local_interface"), "neighbors": []}

                if match.group("remote_port_type") == "ifname":
                    rps = 5
                    remote_port = remote_if

                if match.group("remote_port_type") == "mac":
                    remote_port = match.group("remote_chassis_id")
                    rps = 3
                if match.group("remote_port_type") == "local":
                    remote_port = remote_if
                    rps = 1

                # print (match.group("remote_port"))
                # see sa/profiles/HP/Comware/get_lldp_neighbors.py
                n = {
                    "remote_capabilities": 20,
                    "remote_chassis_id": match.group("remote_id"),
                    "remote_chassis_id_subtype": 4,
                    # "remote_port": match.group("remote_chassis_id"),
                    # "remote_port": match.group("remote_port"),
                    "remote_port": remote_port,
                    "remote_port_subtype": rps,
                    "remote_system_name": match.group("remote_system_name"),
                }

                i["neighbors"] += [n]
                r += [i]

            return r


"""
    # ladvdc -b -C
    INTERFACE_0='eth1'
    HOSTNAME_0='xxxxxx.san.ru'
    PORTNAME_0='GigabitEthernet1/0/1'
    PROTOCOL_0='CDP'
    ADDR_INET4_0='10.11.22.22'
    ADDR_INET6_0=''
    ADDR_802_0=''
    CAPABILITIES_0='S'
    TTL_0='180'
    HOLDTIME_0='160'
    INTERFACE_1='eth0'
    HOSTNAME_1='xxxxxx.san.ru'
    PORTNAME_1='GigabitEthernet2/0/1'
    PROTOCOL_1='CDP'
    ADDR_INET4_1='10.11.22.22'
    ADDR_INET6_1=''
    ADDR_802_1=''
    CAPABILITIES_1='S'
    TTL_1='180'
    HOLDTIME_1='160'



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
