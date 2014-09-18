## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LLDP Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.lib.validators import is_int
from noc.sa.interfaces.base import InterfaceTypeError


class LLDPLinkDiscoveryJob(LinkDiscoveryJob):
    """
    Abstract class for link discovery jobs
    """
    name = "lldp_discovery"
    map_task = "get_lldp_neighbors"
    method = "lldp"
    ignored = not config.getboolean("lldp_discovery", "enabled")
    initial_submit_interval = config.getint("lldp_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("lldp_discovery",
        "initial_submit_concurrency")

    def process_result(self, object, result):
        self.n_cache = {}  # (chassis_id, chassis_subtype) -> object
        for n in result:
            if len(n["neighbors"]) != 1:
                ## Not direct link
                continue
            # Resolve remote object
            ni = n["neighbors"][0]
            remote_object = self.get_neighbor(
                ni["remote_chassis_id"], ni["remote_chassis_id_subtype"])
            self.debug("get_neighbor(%s, %s) -> %s" % (ni["remote_chassis_id"],
                ni["remote_chassis_id_subtype"], remote_object))
            if not remote_object:
                # Object not found
                continue
            # Resolve remote interface
            remote_port = self.get_remote_port(remote_object,
                ni["remote_port"], ni["remote_port_subtype"])
            self.submit_candidate(
                n["local_interface"], remote_object, remote_port)

    def get_neighbor(self, chassis_id, chassis_subtype):
        """
        Find neighbor by chassis id and chassis subtype
        :param chassis_id:
        :param chassis_subtype:
        :return:
        """
        # Get cached
        n = self.n_cache.get((chassis_id, chassis_subtype))
        if n:
            return n
        # Find by id
        f = {
            4: self.get_neighbor_by_mac,  # macAddress(4)
            5: self.get_neighbor_by_ip,  # networkAddress(5)
            7: self.get_neighbor_by_local  # local(7)
        }.get(chassis_subtype)
        if f:
            n = f(chassis_id)
        else:
            n = None
        self.n_cache[(chassis_id, chassis_subtype)] = n
        return n

    def get_neighbor_by_ip(self, ip):
        d = DiscoveryID.objects.filter(router_id=ip).first()
        if d:
            return d.object
        else:
            return None

    def get_neighbor_by_local(self, local):
        pass

    def get_remote_port(self, object, remote_port, remote_port_subtype):
        f = {
            1: self.get_remote_port_by_description,  # interfaceAlias(1)
            3: self.get_remote_port_by_mac,          # macAddress(3)
            5: self.get_remote_port_by_name,         # interfaceName(5)
            7: self.get_remote_port_by_local,        # local(7)
            128: self.get_remote_port_unspecified    # undetermined
        }.get(remote_port_subtype)
        if f:
            return f(object, remote_port)
        else:
            self.info(
                "Unsupported remote port subtype "
                "from %s. value=%s subtype=%s" % (
                object, remote_port, remote_port_subtype))
            return None

    def get_remote_port_by_name(self, object, port):
        return object.profile.convert_interface_name(port)

    def get_remote_port_by_description(self, object, port):
        """
        Find remote port by interface description.
        :param object:
        :param port:
        :return: port name if found, None otherwise.
        """
        try:
            i = Interface.objects.filter(
                managed_object=object.id, description=port).first()
            if i:
                return i.name
            else:
                return None
        except:
            return None

    def get_remote_port_by_local(self, object, port):
        """
        Try to guess remote port from free-form description
        :param object:
        :param port:
        :return:
        """
        # Try ifindex
        if is_int(port):
            i = Interface.objects.filter(
                managed_object=object.id, ifindex=int(port)).first()
            if i:
                return i.name
        # Try interface name
        try:
            n_port = object.profile.convert_interface_name(port)
            i = Interface.objects.filter(
                managed_object=object.id, name=n_port).first()
            if i:
                return n_port
            for p in object.profile.get_interface_names(n_port):
                i = Interface.objects.filter(
                    managed_object=object.id, name=p).first()
                if i:
                    return p
        except InterfaceTypeError:
            pass
        # Unable to decode
        self.info("Unable to decode local subtype port id %s at %s" % (
            port, object))
        return port

    def get_remote_port_by_mac(self, object, mac):
        i = Interface.objects.filter(managed_object=object.id,
            mac=mac).first()
        if i:
            return i.name
        else:
            return None

    def get_remote_port_unspecified(self, object, port):
        """
        Try to guess remote port from description of undetermined subtype.
        :param object:
        :param port:
        :return:
        """
        # Try to find interface with given name.
        try:
            n_port = self.get_remote_port_by_name(object, port)
        except:
            n_port = None
        iface = None
        # Check whether returned port name exists. Return it if yes.
        if n_port:
            i = Interface.objects.filter(
                managed_object=object.id, name=n_port).first()
            if i:
                iface = n_port
        if iface:
            return iface
        # Try to find interface with given MAC address. TODO: clean MAC.
        try:
            iface = self.get_remote_port_by_mac(object, port)
        except:
            iface = None
        if iface:
            return iface
        # Try to find interface with given description.
        iface = self.get_remote_port_by_description(object, port)
        if iface:
            return iface
        # Use algorithms from get_remote_port_by_local as last resort.
        return self.get_remote_port_by_local(object, port)
