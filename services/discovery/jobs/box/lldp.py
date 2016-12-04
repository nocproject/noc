# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LLDP check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.lib.validators import is_ipv4, is_int
from noc.sa.interfaces.base import MACAddressParameter, InterfaceTypeError
from noc.inv.models.interface import Interface


class LLDPCheck(TopologyDiscoveryCheck):
    """
    OAM Topology discovery
    """
    name = "lldp"
    required_script = "get_lldp_neighbors"
    required_capabilities = ["Network | LLDP"]

    CHASSIS_SUBTYPE_MAC = 4
    CHASSIS_SUBTYPE_NETWORK_ADDRESS = 4
    CHASSIS_SUBTYPE_LOCAL = 7

    PORT_SUBTYPE_ALIAS = 1
    PORT_SUBTYPE_MAC = 3
    PORT_SUBTYPE_NAME = 5
    PORT_SUBTYPE_LOCAL = 7
    PORT_SUBTYPE_UNSPECIFIED = 128

    def iter_neighbors(self, mo):
        result = mo.scripts.get_lldp_neighbors()
        self.n_cache = {}  # (chassis_id, chassis_subtype) -> object
        for n in result:
            if len(n["neighbors"]) == 1:
                nn = n["neighbors"][0]
                yield n["local_interface"], nn, nn

    def get_neighbor(self, neighbor_id):
        """
        Neighbor id is an lldp neighbor dict
        """
        chassis_subtype = neighbor_id["remote_chassis_id_subtype"]
        chassis_id = neighbor_id["remote_chassis_id"]
        if chassis_subtype == self.CHASSIS_SUBTYPE_MAC:
            return self.get_neighbor_by_mac(chassis_id)
        elif chassis_subtype == self.CHASSIS_SUBTYPE_NETWORK_ADDRESS:
            return self.get_neighbor_by_ip(chassis_id)
        elif chassis_subtype == self.CHASSIS_SUBTYPE_LOCAL:
            return self.get_neighbor_by_local(chassis_id)
        else:
            self.logger.debug(
                "Cannot find neighbor '%s'. Unsupported subtype %s",
                chassis_id, chassis_subtype
            )
            return None

    def get_neighbor_by_local(self, local):
        """
        Try to find neighbor using arbitrary data
        """
        # Check IPv4
        if is_ipv4(local):
            n = self.get_neighbor_by_ip(local)
            if n:
                return n
        else:
            # Check MAC
            try:
                mac = MACAddressParameter().clean(local)
                n = self.get_neighbor_by_mac(mac)
                if n:
                    return n
            except InterfaceTypeError:
                pass
        # Fallback to hostname
        return self.get_neighbor_by_hostname(local)

    def get_remote_interface(self, remote_object, port_id):
        """
        port id is a lldp neighbor dict
        """
        port_subtype = port_id["remote_port_subtype"],
        port = port_id["remote_port"]
        if port_subtype == self.PORT_SUBTYPE_ALIAS:
            rp = self.get_interface_by_description(port, remote_object)
        elif port_subtype == self.PORT_SUBTYPE_MAC:
            rp = self.get_interface_by_mac(port, remote_object)
        elif port_subtype == self.PORT_SUBTYPE_NAME:
            rp = self.get_interface_by_name(port, remote_object)
        elif port_subtype == self.PORT_SUBTYPE_LOCAL:
            rp = self.get_interface_by_local(port, remote_object)
        elif port_subtype == self.PORT_SUBTYPE_UNSPECIFIED:
            rp = None  # Process below
        else:
            self.logger.debug(
                "Cannot find remote port %r. "
                "Unsupported remote port subtype %s",
                port, port_subtype
            )
            return None
        if not rp:
            self.logger.debug(
                "Trying to guess remote port %s:%r "
                "using unspecified subtype",
                remote_object.name, port
            )
            rp = self.get_interface_by_unspecified(port, remote_object)
        if rp:
            rp = rp.name
        return rp

    def get_interface_by_description(self, port, object):
        """
        Find remote port by interface description.
        :param object:
        :param port:
        :return: port name if found, None otherwise.
        """
        self.logger.debug("Searching port by description: %s:%s", object.name, port)
        try:
            i = Interface.objects.filter(
                managed_object=object.id, description=port)[:2]
            if len(i) == 1:
                return i[0]
            else:
                return None
        except:
            return None

    def get_interface_by_local(self, port, object):
        """
        Try to guess remote port from free-form description
        :param object:
        :param port:
        :return:
        """
        self.logger.debug("Searching port by local: %s:%s", object.name, port)
        # Try ifindex
        if is_int(port):
            i = Interface.objects.filter(
                managed_object=object.id,
                ifindex=int(port)
            ).first()
            if i:
                return i
        # Try interface name
        try:
            n_port = object.profile.convert_interface_name(port)
            i = Interface.objects.filter(
                managed_object=object.id,
                name=n_port
            ).first()
            if i:
                return i
            for p in object.profile.get_interface_names(n_port):
                i = Interface.objects.filter(
                    managed_object=object.id, name=p).first()
                if i:
                    return i
        except InterfaceTypeError:
            pass
        # Unable to decode
        self.logger.info(
            "Unable to decode local subtype port id %s at %s",
            port, object
        )
        return None

    def get_interface_by_unspecified(self, port, object):
        """
        Try to guess remote port from description of undetermined subtype.
        :param object:
        :param port:
        :return:
        """
        self.logger.debug("Searching port by unspecified: %s:%s", object.name, port)
        # Try to find interface with given name.
        try:
            iface = self.get_interface_by_name(port, object)
            if iface:
                return iface
        except ValueError:
            pass
        # Try to find interface with given MAC address. TODO: clean MAC.
        iface = self.get_interface_by_mac(port, object)
        if iface:
            return iface
        # Try to find interface with given description.
        iface = self.get_interface_by_description(port, object)
        if iface:
            return iface
        # Use algorithms from get_remote_port_by_local as last resort.
        return self.get_interface_by_local(port, object)
