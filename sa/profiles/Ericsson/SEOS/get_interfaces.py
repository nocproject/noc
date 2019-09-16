# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.SEOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import time

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mac import MAC
from noc.core.ip import IPv4
from noc.core.validators import is_mac


class Script(BaseScript):
    name = "Ericsson.SEOS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    INTERFACE_TYPES = {
        1: "physical",
        6: "physical",  # ethernetCsmacd
        18: "physical",  # E1 - ds1
        23: "physical",  # ppp
        24: "loopback",  # softwareLoopback
        117: "physical",  # gigabitEthernet
        131: "tunnel",  # tunnel
        135: "SVI",  # l2vlan
        161: "aggregated",  # ieee8023adLag
        53: "SVI",  # propVirtual
        54: "physical",  # propMultiplexor
    }

    def execute_snmp(self, interface=None):
        # v = self.scripts.get_interface_status_ex()
        index = self.scripts.get_ifindexes()
        # index = self.get_ifindexes()
        ifaces = dict((index[i], {"interface": i}) for i in index)
        # Apply ifAdminStatus
        self.apply_table(ifaces, "IF-MIB::ifAdminStatus", "admin_status", lambda x: x == 1)
        # Apply ifOperStatus
        self.apply_table(ifaces, "IF-MIB::ifOperStatus", "oper_status", lambda x: x == 1)
        # Apply PhysAddress
        self.apply_table(ifaces, "IF-MIB::ifPhysAddress", "mac_address")
        self.apply_table(ifaces, "IF-MIB::ifType", "type")
        self.apply_table(ifaces, "IF-MIB::ifSpeed", "speed")
        self.apply_table(ifaces, "IF-MIB::ifMtu", "mtu")
        time.sleep(10)
        self.apply_table(ifaces, "IF-MIB::ifAlias", "description")
        ip_ifaces = self.get_ip_ifaces()
        r = []
        subs = defaultdict(list)
        """
        IF-MIB::ifPhysAddress.1 = STRING:
        IF-MIB::ifPhysAddress.2 = STRING: 0:21:5e:40:c2:50
        IF-MIB::ifPhysAddress.3 = STRING: 0:21:5e:40:c2:52
        """
        for l in ifaces:
            iface = ifaces[l]
            i_type = self.get_interface_type(iface["type"])
            i = {
                "name": iface["interface"],
                "description": self.convert_description(iface.get("description", "")),
                "type": i_type,
                "admin_status": iface["admin_status"] if iface.get("admin_status") else False,
                "oper_status": iface["oper_status"]
                if iface.get("oper_status")
                else iface["admin_status"]
                if iface.get("admin_status")
                else False,
                "snmp_ifindex": l,
            }
            if iface.get("mac_address") and is_mac(iface["mac_address"]):
                i["mac"] = MAC(iface["mac_address"])
            r += [i]
        for l in r:
            if l["name"] in subs:
                l["subinterfaces"] = subs[l["name"]]
            else:
                l["subinterfaces"] = [
                    {
                        "name": l["name"],
                        "description": self.convert_description(l.get("description", "")),
                        "type": "SVI",
                        "enabled_afi": ["BRIDGE"]
                        if l["type"] in ["physical", "aggregated"]
                        else [],
                        "admin_status": l["admin_status"],
                        "oper_status": l["oper_status"],
                        "snmp_ifindex": l["snmp_ifindex"],
                    }
                ]
                if l["snmp_ifindex"] in ip_ifaces:
                    l["subinterfaces"][-1]["ipv4_addresses"] = [IPv4(*ip_ifaces[l["snmp_ifindex"]])]
                    l["subinterfaces"][-1]["enabled_afi"] = ["IPv4"]
        return [{"interfaces": r}]
