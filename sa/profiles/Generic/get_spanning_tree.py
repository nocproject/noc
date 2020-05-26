# ---------------------------------------------------------------------
# Generic.get_spanning_tree
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Dict

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetspanningtree import IGetSpanningTree
from noc.core.mib import mib
from noc.core.snmp.render import render_bin
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Generic.get_spanning_tree"
    interface = IGetSpanningTree

    state_map = {
        1: "disabled",
        2: "blocking",
        3: "listening",
        4: "learning",
        5: "forwarding",
        6: "broken",
    }

    def get_bridge_ifindex_mappings(self) -> Dict[int, int]:
        """
        Getting mappings for bridge port number -> ifindex
        :return:
        """
        pid_ifindex_mappings = {}
        for oid, v in self.snmp.getnext(
            mib["BRIDGE-MIB::dot1dBasePortIfIndex"],
            # max_repetitions=self.get_max_repetitions(),
            # max_retries=self.get_getnext_retires(),
            # timeout=self.get_snmp_timeout(),
        ):
            pid_ifindex_mappings[oid.split(".")[-1]] = v
        return pid_ifindex_mappings

    def execute_rstp(self):
        bridge_ifindex_mappings = self.get_bridge_ifindex_mappings()
        interface_mappings = {
            x["ifindex"]: x["interface"]
            for x in self.scripts.get_interface_properties(enable_ifindex=True)
        }
        root_id = self.snmp.get(
            mib["BRIDGE-MIB::dot1dStpDesignatedRoot", 0],
            display_hints={mib["BRIDGE-MIB::dot1dStpDesignatedRoot"]: render_bin},
        )
        root_p, root_id = root_id[:2], root_id[2:]
        root_priority = self.snmp.get(mib["BRIDGE-MIB::dot1dStpPriority", 0])
        bridge_id = self.snmp.get(mib["BRIDGE-MIB::dot1dBaseBridgeAddress", 0])
        bridge_priority = self.snmp.get(mib["BRIDGE-MIB::dot1dStpPriority", 0])
        ifaces = []
        for stp_port, priority, state, role, d_root, d_bridge, d_port in self.snmp.get_tables(
            [
                mib["BRIDGE-MIB::dot1dStpPortPriority"],
                mib["BRIDGE-MIB::dot1dStpPortState"],
                mib["BRIDGE-MIB::dot1dStpPortEnable"],
                mib["BRIDGE-MIB::dot1dStpPortDesignatedRoot"],
                mib["BRIDGE-MIB::dot1dStpPortDesignatedBridge"],
                mib["BRIDGE-MIB::dot1dStpPortDesignatedPort"],
            ],
            display_hints={
                mib["BRIDGE-MIB::dot1dStpPortDesignatedRoot"]: render_bin,
                mib["BRIDGE-MIB::dot1dStpPortDesignatedBridge"]: render_bin,
                mib["BRIDGE-MIB::dot1dStpPortDesignatedPort"]: render_bin,
            },
        ):
            d_priority, d_bridge = d_bridge[:2], d_bridge[2:]
            ifaces += [
                {
                    # Interface name
                    "interface": interface_mappings[bridge_ifindex_mappings[stp_port]],
                    # Local port id
                    "port_id": "%d.%s" % (priority, stp_port),
                    # Interface state
                    "state": self.state_map[state],
                    # Interface role
                    "role": "disabled",
                    # Port priority
                    "priority": priority,
                    # Designated bridge ID
                    "designated_bridge_id": MAC(d_bridge),
                    # Designated bridge priority
                    "designated_bridge_priority": int("%02X%02X" % tuple(d_priority), 16),
                    # Designated port id
                    "designated_port_id": "%02d.%02d" % tuple(d_port),
                    # P2P indicator
                    "point_to_point": False,
                    # MSTP EdgePort
                    "edge": False,
                }
            ]
        return {
            "mode": "RSTP",
            "instances": [
                {
                    "id": 0,
                    "vlans": "1-4095",
                    "root_id": MAC(root_id),
                    # Root bridge priority
                    "root_priority": root_priority,
                    # Bridge ID
                    "bridge_id": bridge_id,
                    # Bridge priority
                    "bridge_priority": bridge_priority,
                    "interfaces": ifaces,
                }
            ],
        }

    def execute_snmp(self, **kwargs):
        return self.execute_rstp()
