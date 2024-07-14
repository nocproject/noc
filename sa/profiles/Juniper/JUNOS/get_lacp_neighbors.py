# ---------------------------------------------------------------------
# Juniper.JUNOS.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors
from noc.core.mib import mib
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Juniper.JUNOS.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_ifname = re.compile(r"^Aggregated interface: (ae\d+)\s*\n", re.MULTILINE)
    rx_neighbor = re.compile(
        r"^\s+(?P<ifname>\S{2}\-\S+\d+)\s+(?P<role>Actor|Partner)\s+"
        r"(?P<sys_prio>\d+)\s+(?P<sys_id>\S+)\s+(?P<port_prio>\d+)\s+"
        r"(?P<port_num>\d+)\s+(?P<port_key>\d+)\s*\n",
        re.MULTILINE,
    )

    BUNDLE_DATA = {
        "p_ifname": mib["IF-MIB::ifDescr"],
        "actor_port_num": mib["IEEE8023-LAG-MIB::dot3adAggPortActorPort"],
        "partner_port_num": mib["IEEE8023-LAG-MIB::dot3adAggPortPartnerAdminPort"],
        "partner_sysid": mib["IEEE8023-LAG-MIB::dot3adAggPortPartnerOperSystemID"],
    }

    def execute_cli(self):
        try:
            v = self.cli("show lacp interfaces")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        ifaces = self.rx_ifname.findall(v)
        for i in ifaces:
            v = self.cli('show interfaces %s extensive | find "LACP info"' % i)
            if "Pattern not found" in v:
                continue
            bundle = []
            for match in self.rx_neighbor.finditer(v):
                if match.group("role") == "Actor":
                    sys_id = match.group("sys_id")
                    ifname, unit = match.group("ifname").split(".")
                    bundle += [{"interface": ifname, "local_port_id": match.group("port_num")}]
                else:
                    bundle[-1].update(
                        {
                            "remote_system_id": match.group("sys_id"),
                            "remote_port_id": match.group("port_num"),
                        }
                    )
            r += [{"lag_id": i[2:], "interface": i, "system_id": sys_id, "bundle": bundle}]
        return r

    def get_port_actor_admin_keys(self):
        res = {}
        for oid, admin_key in self.snmp.getnext(
            mib["IEEE8023-LAG-MIB::dot3adAggPortActorAdminKey"]
        ):
            ifindex = oid.split(".")[-1]
            res[admin_key] = res.get(admin_key, []) + [ifindex]
        return res

    def get_bundle(self, admin_keys, admin_key):
        res = []
        for index in admin_keys[admin_key]:
            bundle_data_dict = {name: f"{oid}.{index}" for name, oid in self.BUNDLE_DATA.items()}
            bundle_data = self.snmp.get(
                bundle_data_dict, display_hints={bundle_data_dict["partner_sysid"]: render_mac}
            )

            res += [
                {
                    "interface": bundle_data["p_ifname"],
                    "local_port_id": bundle_data["actor_port_num"],
                    "remote_system_id": bundle_data["partner_sysid"],
                    "remote_port_id": bundle_data["partner_port_num"],
                }
            ]
        return res

    def execute_snmp(self):
        res = []
        port_actor_admin_keys = self.get_port_actor_admin_keys()

        for oid, iftype in self.snmp.getnext(mib["IF-MIB::ifType"]):
            if iftype == 161:  # ieee8023adLag(161)
                ifindex = oid.split(".")[-1]
                if self.snmp.get(mib["IF-MIB::ifOperStatus", ifindex]) == 1:  # up(1), down(2)
                    ifname = self.snmp.get(mib["IF-MIB::ifDescr", ifindex])
                    lag_id = ifname[2:]

                    if "." in lag_id:
                        continue

                    actor_admin_key = self.snmp.get(
                        mib["IEEE8023-LAG-MIB::dot3adAggActorAdminKey", ifindex]
                    )
                    sysid = self.snmp.get(
                        mib["IEEE8023-LAG-MIB::dot3adAggActorSystemID", ifindex],
                        display_hints={
                            mib["IEEE8023-LAG-MIB::dot3adAggActorSystemID", ifindex]: render_mac
                        },
                    )
                    bundle = self.get_bundle(port_actor_admin_keys, actor_admin_key)

                    res += [
                        {
                            "lag_id": lag_id,
                            "interface": ifname,
                            "system_id": sysid,
                            "bundle": bundle,
                        }
                    ]
        return res
