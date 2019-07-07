# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import six
from itertools import compress
from binascii import hexlify

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
from noc.core.mib import mib


class Script(BaseScript):
    name = "Generic.get_switchport"
    interface = IGetSwitchport

    def get_iface_portid_mapping(self):
        # Get PID -> ifindex mapping
        r = {}
        for oid, v in self.snmp.getnext(mib["BRIDGE-MIB::dot1dBasePortIfIndex"]):
            r[oid.split(".")[-1]] = v
        return r

    def execute_snmp(self, **kwargs):
        result = {}
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        # Get PID -> ifindex mapping
        pid_ifindex_mappings = self.get_iface_portid_mapping()
        iface_list = sorted(pid_ifindex_mappings, key=int)

        # Getting PVID
        for oid, pvid in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qPvid"]):
            if not pvid:
                # if pvid is 0
                continue
            o = oid.split(".")[-1]
            # pvid[pid_ifindex_mappings[o]] = v
            result[o] = {
                "interface": names[pid_ifindex_mappings[o]],
                "status": False,
                # "ifindex": ifindex,
                # "port_type": port_type,
                "untagged": pvid,
                "tagged": [],
                "members": [],
            }

        # Getting Tagged
        decode_ports_list = {}
        for oid, ports_list in self.snmp.getnext(mib["Q-BRIDGE-MIB::dot1qVlanCurrentEgressPorts"]):
            vlan_num = int(oid.split(".")[-1])
            ports_list = hexlify(ports_list)
            if ports_list not in decode_ports_list:
                ports_list_mask = ["{0:04b}".format(int(x, 16)) for x in ports_list]
                decode_ports_list[ports_list] = list(
                    compress(iface_list, [int(x) for x in "".join(ports_list_mask)])
                )
            for p in decode_ports_list[ports_list]:
                if vlan_num == result[p]["untagged"]:
                    # Perhaps port is switchport @todo getting port type
                    continue
                result[p]["tagged"] += [vlan_num]

        return list(six.itervalues(result))
