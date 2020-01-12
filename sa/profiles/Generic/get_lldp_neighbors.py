# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import six
from six.moves import zip

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC
from noc.core.mib import mib
from noc.core.lldp import (
    LLDP_PORT_SUBTYPE_ALIAS,
    LLDP_PORT_SUBTYPE_MAC,
    LLDP_PORT_SUBTYPE_LOCAL,
    LLDP_PORT_SUBTYPE_COMPONENT,
    LLDP_CHASSIS_SUBTYPE_MAC,
)
from noc.core.comp import smart_bytes


class Script(BaseScript):
    name = "Generic.get_lldp_neighbors"
    cache = True
    interface = IGetLLDPNeighbors

    # Lookup from different tables if port type is `Iface alias`
    # 1 - LLDP-MIB::lldpLocPortId
    # 2 - LLDP-MIB::lldpLocPortDesc
    LLDP_PORT_TABLE = 2

    def get_interface_alias(self, port_id, port_descr):
        if self.LLDP_PORT_TABLE == 1:
            return port_id
        else:
            return port_descr

    def get_local_iface(self):
        r = {}
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        # Get LocalPort Table
        for port_num, port_subtype, port_id, port_descr in self.snmp.get_tables(
            [
                mib["LLDP-MIB::lldpLocPortIdSubtype"],
                mib["LLDP-MIB::lldpLocPortId"],
                mib["LLDP-MIB::lldpLocPortDesc"],
            ],
            max_retries=1,
        ):
            if port_subtype == LLDP_PORT_SUBTYPE_ALIAS:
                # Iface alias
                iface_name = self.get_interface_alias(port_id, port_descr)
            elif port_subtype == LLDP_PORT_SUBTYPE_MAC:
                # Iface MAC address
                raise NotImplementedError()
            elif port_subtype == LLDP_PORT_SUBTYPE_LOCAL and port_id.isdigit():
                # Iface local (ifindex)
                iface_name = names[int(port_id)]
            else:
                # Iface local
                iface_name = port_id
            r[port_num] = {"local_interface": iface_name, "local_interface_subtype": port_subtype}
        if not r:
            self.logger.warning(
                "Not getting local LLDP port mappings. Check 1.0.8802.1.1.2.1.3.7 table"
            )
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
        if self.has_snmp():
            for v in self.snmp.get_tables(
                [
                    mib["LLDP-MIB::lldpRemLocalPortNum"],
                    mib["LLDP-MIB::lldpRemChassisIdSubtype"],
                    mib["LLDP-MIB::lldpRemChassisId"],
                    mib["LLDP-MIB::lldpRemPortIdSubtype"],
                    mib["LLDP-MIB::lldpRemPortId"],
                    mib["LLDP-MIB::lldpRemPortDesc"],
                    mib["LLDP-MIB::lldpRemSysName"],
                ],
                bulk=True,
                max_retries=1,
            ):
                if v:
                    neigh = dict(zip(neighb, v[2:]))
                    # cleaning
                    if neigh["remote_port_subtype"] == LLDP_PORT_SUBTYPE_COMPONENT:
                        neigh["remote_port_subtype"] = LLDP_PORT_SUBTYPE_ALIAS
                    neigh["remote_port"] = smart_bytes(neigh["remote_port"]).replace(b" \x00", b"")
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
                        neigh["remote_port"] = neigh["remote_port"].replace(b"\x00", b"")
                    if "remote_system_name" in neigh:
                        neigh["remote_system_name"] = neigh["remote_system_name"].rstrip(b"\x00")
                    if "remote_port_description" in neigh:
                        neigh["remote_port_description"] = neigh["remote_port_description"].rstrip(
                            b"\x00"
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
