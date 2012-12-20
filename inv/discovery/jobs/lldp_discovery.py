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
            self.debug("get_neighbor(%s, %s) -> %s" % (ni["remote_chassis_id"], ni["remote_chassis_id_subtype"], remote_object))
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

    def get_neighbor_by_mac(self, mac):
        """
        Find neighbor by MAC address
        :param mac:
        :return:
        """
        d = DiscoveryID.objects.filter(first_chassis_mac__lte=mac,
            last_chassis_mac__gte=mac).first()
        if d:
            return d.object
        else:
            return None

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
            5: self.get_remote_port_by_name,  # interfaceName(5)
            7: self.get_remote_port_by_name   # local(7)
        }.get(remote_port_subtype)
        if f:
            return f(object, remote_port)
        else:
            return None

    def get_remote_port_by_name(self, object, port):
        return object.profile.convert_interface_name(port)
