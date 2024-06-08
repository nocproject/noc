# ---------------------------------------------------------------------
# HP.ProCurve.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_PORT_SUBTYPE_LOCAL,
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
    name = "HP.ProCurve.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_localport = re.compile(r"^\s*(\S+)\s*\|\s*local\s+(\d+)\s+.+?$", re.MULTILINE)
    rx_split = re.compile(r"^\s*----.+?\n", re.MULTILINE)
    rx_line = re.compile(r"^\s*(?P<port>\S+)\s*|", re.MULTILINE)
    # rx_chassis_id=re.compile(r"^\s*ChassisId\s*:\s*(.{17})",re.MULTILINE|re.DOTALL|re.IGNORECASE)
    rx_chassis_id = re.compile(
        r"^\s*ChassisType\s*:\s*(\S+)\s*\n^\s*ChassisId\s*:\s*([a-zA-Z0-9\.\- ]+)\s*\n",
        re.MULTILINE,
    )
    rx_port_id = re.compile(
        r"^\s*PortType\s*:\s*(\S+)\s*\n^\s*PortId\s*:\s*(.+?)\s*\n", re.MULTILINE
    )
    rx_sys_name = re.compile(r"^\s*SysName\s*:\s*(?P<sys_name>.+)\s*\n", re.MULTILINE)
    rx_sys_descr = re.compile(r"^\s*System Descr\s*:\s*(?P<sys_descr>.+)\s*\n", re.MULTILINE)
    rx_port_descr = re.compile(r"^\s*PortDescr\s*:\s*(?P<port_descr>.+)\s*\n", re.MULTILINE)
    rx_cap = re.compile(r"^\s*System Capabilities Enabled\s*:(.*?)$", re.MULTILINE)

    def execute_cli(self):
        r = []
        # HP.ProCurve advertises local(7) port sub-type, so local_interface_id parameter required
        # Collect data
        local_port_ids = {}  # name -> id
        for port, local_id in self.rx_localport.findall(self.cli("show lldp info local-device")):
            local_port_ids[port] = int(local_id)
        # Get neighbors
        v = self.cli("show lldp info remote-device")
        for ln in self.rx_split.split(v)[1].splitlines():
            ln = ln.strip()
            if not ln:
                continue
            match = self.rx_line.search(ln)
            if not match:
                continue
            local_interface = match.group("port")
            i = {"local_interface": local_interface, "neighbors": []}
            # Add locally assigned port id, if exists
            if local_interface in local_port_ids:
                i["local_interface_id"] = local_port_ids[local_interface]
            v = self.cli("show lldp info remote-device %s" % local_interface)
            # Get chassis id
            match = self.rx_chassis_id.search(v)
            if not match:
                continue
            remote_chassis_id_subtype = {
                "mac-address": LLDP_CHASSIS_SUBTYPE_MAC,
                "network-address": LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
                "local": LLDP_CHASSIS_SUBTYPE_LOCAL,
            }[match.group(1)]
            remote_chassis_id = match.group(2).strip().replace(" ", "")
            if remote_chassis_id_subtype == LLDP_CHASSIS_SUBTYPE_MAC:
                remote_chassis_id = MAC(remote_chassis_id)
            else:
                remote_chassis_id = remote_chassis_id.strip()
            # Get remote port
            match = self.rx_port_id.search(v)
            if not match:
                continue
            remote_port_subtype = {
                "interface-alias": LLDP_PORT_SUBTYPE_ALIAS,
                "mac-address": LLDP_PORT_SUBTYPE_MAC,
                "network-address": LLDP_PORT_SUBTYPE_NETWORK_ADDRESS,
                "interface-name": LLDP_PORT_SUBTYPE_NAME,
                "inte...": LLDP_PORT_SUBTYPE_NAME,  # Found in 2910al ver. W.14.38
                "local": LLDP_PORT_SUBTYPE_LOCAL,
            }[match.group(1)]
            remote_port = match.group(2).strip().replace(" ", "")
            if remote_port_subtype == LLDP_PORT_SUBTYPE_MAC:
                remote_port = MAC(remote_port)
            else:
                remote_chassis_id = remote_chassis_id.strip()
            n = {
                "remote_chassis_id": remote_chassis_id,
                "remote_chassis_id_subtype": remote_chassis_id_subtype,
                "remote_port": remote_port,
                "remote_port_subtype": remote_port_subtype,
            }
            # Get remote system name
            match = self.rx_sys_name.search(v)
            if match:
                n["remote_system_name"] = match.group("sys_name").strip()
            # Get remote system description
            match = self.rx_sys_descr.search(v)
            if match:
                n["remote_system_description"] = match.group("sys_descr").strip()
            # Get remote port description
            match = self.rx_port_descr.search(v)
            if match:
                n["remote_port_description"] = match.group("port_descr").strip()
            # Get capabilities
            caps = 0
            match = self.rx_cap.search(v)
            if match:
                caps = lldp_caps_to_bits(
                    match.group(1).strip().split(", "),
                    {
                        "other": LLDP_CAP_OTHER,
                        "repeater": LLDP_CAP_REPEATER,
                        "bridge": LLDP_CAP_BRIDGE,
                        "wlanaccesspoint": LLDP_CAP_WLAN_ACCESS_POINT,
                        "wlan-access-point": LLDP_CAP_WLAN_ACCESS_POINT,
                        "router": LLDP_CAP_ROUTER,
                        "telephone": LLDP_CAP_TELEPHONE,
                        "docsis": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                        "station": LLDP_CAP_STATION_ONLY,
                        "station-only": LLDP_CAP_STATION_ONLY,
                    },
                )
            n["remote_capabilities"] = caps
            i["neighbors"] += [n]
            r += [i]
        return r
