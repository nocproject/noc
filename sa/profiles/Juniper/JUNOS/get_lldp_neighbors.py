# ---------------------------------------------------------------------
# Juniper.JUNOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.base import IntParameter
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_int
from noc.core.mib import mib
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    LLDP_CAP_DOCSIS_CABLE_DEVICE,
    LLDP_CAP_STATION_ONLY,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "Juniper.JUNOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    #
    # EX Series
    #
    rx_localport = re.compile(r"^(\S+)\s+(?:(?:ae\d+|\-)\s+)?(\d+)\s+\S+\s+?Up.+$", re.MULTILINE)
    rx_neigh = re.compile(r"^(?P<local_if>[x,g]e-\S+|me\d(\.\d)?|fxp0|et-\S+)\s.*?$", re.MULTILINE)
    # If <p_type>=='Interface alias', then <p_id> will match 'Port description'
    # else it will match 'Port ID'
    rx_detail = re.compile(
        r"Chassis type\s+:\s+(?P<ch_type>.+)\n"
        r"Chassis ID\s+:\s(?P<id>\S+)\n"
        r"Port type\s+:\s(?P<p_type>.+)\n"
        r"(Port ID\s+:\s(?P<p_id>.+)\n)?"
        r"(Port description\s+:\s(?P<p_descr>.+)\n)?"
        r"(System name\s+:\s(?P<name>.+)\n)?",
        re.MULTILINE,
    )
    rx_caps = re.compile(
        r"System capabilities\s*\n\s*Supported\s*:\s(?P<capability>.+)\n", re.MULTILINE
    )
    rx_mgmt = re.compile(
        r"Management address\s*\n"
        r"\s+Address Type\s+:\s*IPv4\(\d+\)\n"
        r"\s+Address\s+:\s*(?P<address>\S+)\n",
        re.MULTILINE,
    )
    CHASSIS_TYPE = {
        "Mac address": LLDP_CHASSIS_SUBTYPE_MAC,
        "Network address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
        "Locally assigned": LLDP_CHASSIS_SUBTYPE_LOCAL,
    }
    PORT_TYPE = {
        "Interface alias": LLDP_PORT_SUBTYPE_ALIAS,
        "Port component": LLDP_PORT_SUBTYPE_COMPONENT,
        "Mac address": LLDP_PORT_SUBTYPE_MAC,
        "Interface name": LLDP_PORT_SUBTYPE_NAME,
        "Locally assigned": LLDP_PORT_SUBTYPE_LOCAL,
    }

    def get_local_iface(self):
        r = {}
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        # Get LocalPort Table
        for v in self.snmp.get_tables(
            [
                mib["LLDP-MIB::lldpLocPortNum"],
                mib["LLDP-MIB::lldpLocPortIdSubtype"],
                mib["LLDP-MIB::lldpLocPortId"],
                mib["LLDP-MIB::lldpLocPortDesc"],
            ]
        ):
            if is_int(v[3]):
                if int(v[3]) not in names:
                    continue
                iface_name = names[int(v[3])]
            else:
                iface_name = v[3]
            if iface_name.endswith(".0"):
                iface_name = iface_name[:-2]
            r[v[0]] = {"local_interface": iface_name, "local_interface_subtype": v[2]}
        return r

    def execute_cli(self):
        if self.is_has_lldp:
            return self.execute_switch()
        raise self.NotSupportedError()

    # Match mx, ex, qfx, acx
    def execute_switch(self):
        r = []
        # Collect data
        local_port_ids = {}  # name -> id
        v = self.cli("show lldp local-information", cached=True)
        for port, local_id in self.rx_localport.findall(v):
            local_port_ids[port] = IntParameter().clean(local_id)
        v = self.cli("show lldp neighbors")
        for match in self.rx_neigh.finditer(v):
            ifname = match.group("local_if")
            v = self.cli("show lldp neighbors interface %s" % ifname)
            n = {}
            match = self.rx_detail.search(v)
            n["remote_chassis_id_subtype"] = self.CHASSIS_TYPE[match.group("ch_type")]
            n["remote_chassis_id"] = match.group("id")
            n["remote_port_subtype"] = self.PORT_TYPE[match.group("p_type")]
            if match.group("p_id"):
                n["remote_port"] = match.group("p_id")
            if match.group("p_descr"):
                n["remote_port_description"] = match.group("p_descr")
            # On some devices we are not seen `Port ID`
            if (
                "remote_port" not in n
                and n["remote_port_subtype"] == 1
                and "remote_port_description" in n
            ):
                n["remote_port"] = n["remote_port_description"]
            elif "remote_port" not in n and "remote_port_description" in n:
                # Juniper.JUNOS mx10-t 11.4X27.62, LOCAL_NAME xe-0/0/0 L3
                n["remote_port"] = n["remote_port_description"]
                n["remote_port_subtype"] = 1
            if match.group("name"):
                n["remote_system_name"] = match.group("name")
            match = self.rx_mgmt.search(v)
            if match:
                n["remote_mgmt_address"] = match.group("address")
            # Get capability
            cap = 0
            match = self.rx_caps.search(v)
            if match:
                s = match.group("capability")
                # WLAN Access Point
                s = s.replace(" Access Point", "")
                # Station Only
                s = s.replace(" Only", "")
                cap = lldp_caps_to_bits(
                    s.strip().split(" "),
                    {
                        "other": LLDP_CAP_OTHER,
                        "repeater": LLDP_CAP_REPEATER,
                        "bridge": LLDP_CAP_BRIDGE,
                        "wlan": LLDP_CAP_WLAN_ACCESS_POINT,
                        "router": LLDP_CAP_ROUTER,
                        "telephone": LLDP_CAP_TELEPHONE,
                        "cable": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "station": LLDP_CAP_STATION_ONLY,
                    },
                )
            n["remote_capabilities"] = cap
            iface_found = False
            for i in r:
                if i["local_interface"] == ifname:
                    i["neighbors"] += [n]
                    iface_found = True
                    break
            if not iface_found:
                i = {"local_interface": ifname, "neighbors": [n]}
                if ifname in local_port_ids:
                    i["local_interface_id"] = local_port_ids[ifname]
                r += [i]
        for q in r:
            if q["local_interface"].endswith(".0"):
                q["local_interface"] = q["local_interface"][:-2]
        return r
