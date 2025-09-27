# ----------------------------------------------------------------------
# NSN.TIMOS.get_lldp_neighbors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_CHASSIS_SUBTYPE_MAC,
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
from noc.core.snmp.render import render_bin


class Script(BaseScript):
    name = "NSN.TIMOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_some = re.compile(r"^(?P<port>((esat-|)\d+/\d+/(c\d+|\d+)(/\d+|/u\d+|)|\w+\/\d+))\s+")

    rx_local_lldp = re.compile(r"""\s+?:\s(?P<local_interface_id>.+?)\s""")
    rx_remote_info = re.compile(
        r"""
        Supported\sCaps\s+:\s(?P<remote_capabilities>.+?)\n
        .*?
        Chassis\sId\sSubtype\s+:\s(?P<remote_chassis_id_subtype>\d)\s
        .*?
        Chassis\sId\s+:\s(?P<remote_chassis_id>\S+)\n
        .*?
        PortId\sSubtype\s+:\s(?P<remote_port_subtype>.)\s
        .*?
        Port\sId\s+:\s(?P<remote_port>.+?)("|Port)
        .*?
        System\sName\s+:\s(?P<remote_system_name>\S+).+
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE,
    )

    @staticmethod
    def fixport(port, port_type):
        # fix alcatel encode port like hex string
        if port_type == "5" and "\n " in port:
            # PortId Subtype        : 5 (interfaceName)
            # Port Id               : 65:73:61:74:2D:32:2F:31:2F:32:31
            #                         "esat-2/1/21"
            #
            # PortId Subtype        : 5 (interfaceName)
            # Port Id               : 58:47:69:67:61:62:69:74:45:74:68:65:72:6E:65:74:30:2F:
            #                         30:2F:34:38
            #                       "XGigabitEthernet0/0/48"
            remote_port_name1, remote_port__name2 = port.rsplit("\n", 1)
            remote_port_name1 = re.sub(r"\n|\s+", "", remote_port_name1)
            return smart_text(codecs.decode(remote_port_name1.strip().replace(":", ""), "hex"))
        if port_type == "7":
            return port.replace("\n", "")
        return port

    def get_port_info(self, port):
        try:
            v = self.cli("show port %s ethernet lldp remote-info" % port)
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        else:
            match_obj = self.rx_remote_info.search(v)
            pri = match_obj.groupdict()
            pri["remote_capabilities"] = lldp_caps_to_bits(
                pri["remote_capabilities"].split(),
                {
                    "other": LLDP_CAP_OTHER,
                    "repeater": LLDP_CAP_REPEATER,
                    "bridge": LLDP_CAP_BRIDGE,
                    "wlanaccesspoint": LLDP_CAP_WLAN_ACCESS_POINT,
                    "router": LLDP_CAP_ROUTER,
                    "telephone": LLDP_CAP_TELEPHONE,
                    "cvlan": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    "station": LLDP_CAP_STATION_ONLY,
                },
            )
            pri["remote_port"] = self.fixport(pri["remote_port"], pri["remote_port_subtype"])
            if "n/a" in pri["remote_system_name"]:
                del pri["remote_system_name"]
            return pri

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show system lldp neighbor")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for line in v.splitlines():
            match = self.rx_some.search(line)
            if not match:
                continue
            port = match.group("port")
            local_lldp = self.cli("show port %s ethernet detail | match IfIndex" % port)
            lldp_match = self.rx_local_lldp.search(local_lldp)
            if not lldp_match:
                continue
            local_interface_id = str(lldp_match.group("local_interface_id"))
            pri = self.get_port_info(port)
            r += [
                {
                    "local_interface": port,
                    "local_interface_id": local_interface_id,
                    "neighbors": [pri],
                }
            ]
        return r

    # get lldp snmp
    # Lookup from different tables if port type is `Iface alias`
    # 1 - LLDP-MIB::lldpLocPortId
    # 2 - LLDP-MIB::lldpLocPortDesc
    LLDP_PORT_TABLE = 2

    def get_interface_alias(self, port_id, port_descr):
        if self.LLDP_PORT_TABLE == 1:
            return port_id
        return port_descr

    def get_local_iface(self):
        r = {}
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_descr in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.6527.3.1.2.59.3.1.1.2",
                "1.3.6.1.4.1.6527.3.1.2.59.3.1.1.3",
                "1.3.6.1.4.1.6527.3.1.2.59.3.1.1.4",
            ],
            max_retries=1,
        ):
            port_num = port_num.split(".")[0]
            if port_subtype == LLDP_PORT_SUBTYPE_ALIAS:
                # Iface alias
                iface_name = self.get_interface_alias(port_id, port_descr)
            elif port_subtype == LLDP_PORT_SUBTYPE_MAC:
                # Iface MAC address
                raise NotImplementedError()
            elif port_subtype == LLDP_PORT_SUBTYPE_LOCAL:
                # Iface local (ifindex)
                iface_name = names[int(port_num)]
            else:
                # Iface local
                iface_name = port_id

            r[port_num] = {"local_interface": iface_name, "local_interface_subtype": port_subtype}
        if not r:
            self.logger.warning("Not getting local LLDP port mappings. Check lldp table")
            raise NotImplementedError()
        return r

    def execute_snmp(self):
        neighb = (
            "remote_chassis_id_subtype",
            "remote_chassis_id",
            "remote_port_subtype",
            "remote_port",
            "remote_port_description",
            "remote_system_name",
        )
        r = []
        local_ports = self.get_local_iface()
        for v in self.snmp.get_tables(
            [
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.2",
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.4",
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.5",
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.6",
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.7",
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.8",
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.9",
            ],
            bulk=False,
            max_retries=1,
            display_hints={
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.7": render_bin,
                "1.3.6.1.4.1.6527.3.1.2.59.4.1.1.5": render_bin,
            },
        ):
            if v:
                neigh = dict(zip(neighb, v[2:]))
                # cleaning
                if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_COMPONENT:
                    neigh["remote_port_subtype"] = LLDP_PORT_SUBTYPE_ALIAS
                neigh["remote_port"] = neigh["remote_port"].replace(b" \x00", b"")
                if neigh["remote_chassis_id_subtype"] == LLDP_CHASSIS_SUBTYPE_MAC:
                    neigh["remote_chassis_id"] = MAC(neigh["remote_chassis_id"])
                if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC:
                    try:
                        neigh["remote_port"] = MAC(neigh["remote_port"])
                    except ValueError:
                        self.logger.warning(
                            "Bad MAC address on Remote Neighbor: %s", neigh["remote_port"]
                        )
                else:
                    neigh["remote_port"] = smart_text(neigh["remote_port"]).rstrip("\x00")
                if "remote_system_name" in neigh:
                    neigh["remote_system_name"] = smart_text(neigh["remote_system_name"]).rstrip(
                        "\x00"
                    )
                if "remote_port_description" in neigh:
                    neigh["remote_port_description"] = neigh["remote_port_description"].rstrip(
                        "\x00"
                    )
                r += [
                    {
                        "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                        # @todo if local interface subtype != 5
                        # "local_interface_id": 5,
                        "neighbors": [neigh],
                    }
                ]
        return r
