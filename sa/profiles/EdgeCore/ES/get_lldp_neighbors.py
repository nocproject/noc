# ---------------------------------------------------------------------
# EdgeCore.ES.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
import binascii

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors, MACAddressParameter
from noc.core.mib import mib
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_MAC,
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
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "EdgeCore.ES.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    always_prefer = "S"

    rx_localport = re.compile(
        r"^\s*Eth(| )(.+?)\s*(\|)MAC Address\s+(\S+).+?$", re.MULTILINE | re.DOTALL
    )
    rx_neigh = re.compile(
        r"(?P<local_if>Eth\s\S+)\s+(\||)\s+(?P<id>\S+).*?(?P<name>\S*)$",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_detail = re.compile(
        r".*Chassis I(d|D)\s+:\s(?P<id>\S+).*?Port(|\s+)ID Type\s+:\s"
        r"(?P<p_type>[^\n]+).*?Port(|\s+)ID\s+:\s(?P<p_id>[^\n]+).*?"
        r"(Sys(|tem\s+)Name\s+:\s(?P<name>\S*)|).*?"
        r"((SystemCapSupported|System\sCapabilities)\s+:\s"
        r"(?P<capability>[^\n]*)|).*",
        re.MULTILINE | re.IGNORECASE | re.DOTALL,
    )
    rx_port_descr = re.compile(r"^\s*Port Description\s+:\s+(?P<descr>.+)\n", re.MULTILINE)
    rx_system_descr = re.compile(r"^\s*System Description\s+:\s+(?P<descr>.+)\n", re.MULTILINE)

    CHASSIS_SUBTYPE = {"Mac Address": LLDP_CHASSIS_SUBTYPE_MAC, "Local": LLDP_CHASSIS_SUBTYPE_LOCAL}
    PORT_SUBTYPE = {
        "Mac Address": LLDP_PORT_SUBTYPE_MAC,
        "Interface Name": LLDP_PORT_SUBTYPE_NAME,
        "Local": LLDP_PORT_SUBTYPE_LOCAL,
    }

    def get_local_iface(self):
        r = {}
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_descr in self.snmp.get_tables(
            [
                mib["LLDP-MIB::lldpLocPortIdSubtype"],
                mib["LLDP-MIB::lldpLocPortId"],
                mib["LLDP-MIB::lldpLocPortDesc"],
            ]
        ):
            if port_subtype == 1:
                # Iface alias
                iface_name = port_id  # BUG. Look in PortID instead PortDesc
            elif port_subtype == 3:
                # Iface MAC address
                iface_name = names.get(int(port_num), port_id)
            elif port_subtype == 7 and port_id.isdigit():
                # Iface local (ifindex)
                iface_name = names[int(port_id)]
            else:
                # Iface local
                iface_name = port_id
            r[port_num] = {"local_interface": iface_name}
        if not r:
            self.logger.warning(
                "Not getting local LLDP port mappings. Check 1.0.8802.1.1.2.1.3.7 table"
            )
            raise NotImplementedError()
        return r

    def execute_cli(self):
        # No lldp on 46xx
        if self.is_platform_46:
            raise self.NotSupportedError()

        ifs = []
        r = []
        # EdgeCore ES3526 advertises MAC address(3) port sub-type,
        # so local_interface_id parameter required Collect data
        local_port_ids = {}  # name -> id
        for port, local_id in self.rx_localport.findall(self.cli("show lldp info local-device")):
            local_port_ids["Eth " + port] = MACAddressParameter().clean(local_id)
        v = self.cli("show lldp info remote-device")
        for match in self.rx_neigh.finditer(v):
            ifs += [{"local_interface": match.group("local_if"), "neighbors": []}]
        for i in ifs:
            if i["local_interface"] in local_port_ids:
                i["local_interface_id"] = local_port_ids[i["local_interface"]]
            v = self.cli("show lldp info remote detail %s" % i["local_interface"])
            match = self.re_search(self.rx_detail, v)
            n = {"remote_chassis_id_subtype": LLDP_CHASSIS_SUBTYPE_MAC}
            if match:
                n["remote_port_subtype"] = {
                    "MAC Address": LLDP_PORT_SUBTYPE_MAC,
                    "Interface name": LLDP_PORT_SUBTYPE_NAME,
                    "Interface Name": LLDP_PORT_SUBTYPE_NAME,
                    "Inerface Alias": LLDP_PORT_SUBTYPE_NAME,
                    "Inerface alias": LLDP_PORT_SUBTYPE_NAME,
                    "Interface Alias": LLDP_PORT_SUBTYPE_NAME,
                    "Interface alias": LLDP_PORT_SUBTYPE_NAME,
                    "Local": LLDP_PORT_SUBTYPE_LOCAL,
                    "Locally Assigned": LLDP_PORT_SUBTYPE_LOCAL,
                    "Locally assigned": LLDP_PORT_SUBTYPE_LOCAL,
                }[match.group("p_type")]
                if n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                    remote_port = MACAddressParameter().clean(match.group("p_id"))
                elif n["remote_port_subtype"] == LLDP_PORT_SUBTYPE_NAME:
                    remote_port = match.group("p_id").strip()
                elif "-" in match.group("p_id"):
                    # Removing bug
                    try:
                        remote_port = binascii.unhexlify("".join(match.group("p_id").split("-")))
                    except TypeError:
                        remote_port = str(match.group("p_id"))
                    remote_port = remote_port.rstrip(smart_text("\x00"))
                else:
                    remote_port = match.group("p_id").strip()
                n["remote_chassis_id"] = match.group("id")
                if match.group("name"):
                    n["remote_system_name"] = match.group("name")
                n["remote_port"] = str(remote_port)
                if match.group("capability"):
                    caps = lldp_caps_to_bits(
                        match.group("capability").strip().split(", "),
                        {
                            "other": LLDP_CAP_OTHER,
                            "repeater": LLDP_CAP_REPEATER,
                            "bridge": LLDP_CAP_BRIDGE,
                            "wlan": LLDP_CAP_WLAN_ACCESS_POINT,
                            "wlan access point": LLDP_CAP_WLAN_ACCESS_POINT,
                            "router": LLDP_CAP_ROUTER,
                            "telephone": LLDP_CAP_TELEPHONE,
                            "cable": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                            "station": LLDP_CAP_STATION_ONLY,
                        },
                    )
                    n["remote_capabilities"] = caps
                match = self.rx_system_descr.search(v)
                if match:
                    n["remote_system_description"] = match.group("descr")
                match = self.rx_port_descr.search(v)
                if match:
                    n["remote_port_description"] = match.group("descr")
            i["neighbors"] += [n]
            r += [i]
        return r
