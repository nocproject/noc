# ---------------------------------------------------------------------
# NSGATE.NIS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.mib import mib


class Script(BaseScript):
    name = "NSGATE.NIS.get_mac_address_table"
    interface = IGetMACAddressTable

    MAX_REPETITIONS = 1

    def get_iface_mapping(self):
        # Get PID -> ifindex mapping
        pid_iface_map = {}
        r = {}
        for oid, v in self.snmp.getnext(
            mib["BRIDGE-MIB::dot1dBasePortIfIndex"],
            max_repetitions=self.get_max_repetitions(),
            max_retries=self.get_getnext_retires(),
            bulk=self.get_bulk(),
        ):
            pid_iface_map[v] = int(oid.split(".")[-1])
        for i in self.scripts.get_interface_properties(enable_ifindex=True):
            if i["ifindex"] not in pid_iface_map:
                self.logger.warning("[%s] Not PID iface mapping: %s", i["interface"], r)
                continue
            r[pid_iface_map[i["ifindex"]]] = i["interface"]
        return r
