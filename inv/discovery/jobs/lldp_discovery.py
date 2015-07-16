## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LLDP Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface
from noc.lib.validators import is_int, is_ipv4
from noc.sa.interfaces.base import (InterfaceTypeError,
                                    MACAddressParameter)


class LLDPLinkDiscoveryJob(LinkDiscoveryJob):
    """
    Abstract class for link discovery jobs
    """
    name = "lldp_discovery"
    map_task = "get_lldp_neighbors"
    method = "lldp"
    ignored = not config.getboolean("lldp_discovery", "enabled")

    def process_result(self, object, result):
        self.n_cache = {}  # (chassis_id, chassis_subtype) -> object
        for n in result:
            if len(n["neighbors"]) != 1:
                ## Not direct link
                continue
            # Resolve remote object
            ni = n["neighbors"][0]
            remote_object = self.get_neighbor(
                ni["remote_chassis_id"],
                ni["remote_chassis_id_subtype"]
            )
            self.logger.debug(
                "get_neighbor(%s, %s) -> %s",
                ni["remote_chassis_id"],
                ni["remote_chassis_id_subtype"],
                remote_object
            )
            if not remote_object:
                # Object not found
                continue
            # Resolve remote interface
            remote_port = self.get_remote_port(
                remote_object,
                ni["remote_port"],
                ni["remote_port_subtype"]
            )
            self.submit_candidate(
                n["local_interface"],
                remote_object,
                remote_port
            )

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

    def get_neighbor_by_hostname(self, name):
        ds = DiscoveryID.objects.filter(hostname=name)[:2]
        if len(ds) == 1:
            # Exactly one neighbor known
            return ds[0].object
        else:
            return None

    def get_neighbor_by_local(self, local):
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

    def get_remote_port(self, object, remote_port, remote_port_subtype):
        f = {
            1: self.get_remote_port_by_description,  # interfaceAlias(1)
            3: self.get_remote_port_by_mac,          # macAddress(3)
            5: self.get_remote_port_by_name,         # interfaceName(5)
            7: self.get_remote_port_by_local,        # local(7)
            128: self.get_remote_port_unspecified    # undetermined
        }.get(remote_port_subtype)
        if f:
            rp = f(object, remote_port)
            if rp:
                return rp
        else:
            self.logger.info(
                "Unsupported remote port subtype "
                "from %s. value=%s subtype=%s."
                "Trying to guess",
                object, remote_port, remote_port_subtype
            )
        if remote_port_subtype != 128:
            self.logger.info(
                "Trying to guess port using unspecified subtype"
            )
            return self.get_remote_port_unspecified(object, remote_port)
        return None

    def get_remote_port_by_name(self, object, port):
        self.debug("Remote port name: %s" % port)
        return object.profile.convert_interface_name(port)

    def get_remote_port_by_description(self, object, port):
        """
        Find remote port by interface description.
        :param object:
        :param port:
        :return: port name if found, None otherwise.
        """
        self.debug("Remote port description: %s" % port)
        try:
            i = Interface.objects.filter(
                managed_object=object.id, description=port)[:2]
            if len(i) == 1:
                return i[0].name
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
        self.debug("Remote port local: %s" % port)
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
        self.debug("Remote port mac: %s" % mac)
        try:
            mac = MACAddressParameter().clean(mac)
        except InterfaceTypeError:
            self.debug("Invalid MAC, ignoring")
            return None
        i = Interface.objects.filter(
            managed_object=object.id,
            mac=mac)[:2]
        if len(i) == 1:
            return i[0].name
        elif len(i) > 1:
            self.debug("Non-unique MAC address: %s. Ignoring" % mac)
        return None

    def get_remote_port_unspecified(self, object, port):
        """
        Try to guess remote port from description of undetermined subtype.
        :param object:
        :param port:
        :return:
        """
        self.debug("Remote port unspecified: %s" % port)
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
