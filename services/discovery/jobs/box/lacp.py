# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CDP check
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class LACPCheck(TopologyDiscoveryCheck):
    """
    CDP Topology discovery
    """
    name = "lacp"
    required_script = "get_lacp_neighbors"
    required_capabilities = ["Network | LACP"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_lacp_neighbors()
        for lag in result:
            for n in lag["bundle"]:
                self.set_interface_alias(mo, n["interface"], n["local_port_id"])
                # We yield local port id instead of real name
                # as we set interface alias
                # Real port name will be set during clean_interface
                yield n["local_port_id"], n["remote_system_id"], n["remote_port_id"]

    get_neighbor = TopologyDiscoveryCheck.get_neighbor_by_mac

    def get_remote_interface(self, remote_object, remote_interface):
        """
        Real values are set by set_interface alias
        :param remote_object:
        :param remote_interface:
        :return:
        """
        return remote_interface
