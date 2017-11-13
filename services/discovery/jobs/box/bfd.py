# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BFD check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class BFDCheck(TopologyDiscoveryCheck):
    """
    BFD Topology discovery
    """
    name = "bfd"
    required_script = "get_bfd_sessions"
    required_capabilities = ["Network | BFD"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_bfd_sessions()
        for n in result:
            self.set_interface_alias(mo, n["local_interface"], n["local_discriminator"])
            # We yield local port id instead of real name
            # as we set interface alias
            # Real port name will be set during clean_interface
            yield n["local_discriminator"], n["remote_address"], n["remote_discriminator"]

    get_neighbor = TopologyDiscoveryCheck.get_neighbor_by_ip

    def get_remote_interface(self, remote_object, remote_interface):
        """
        Real values are set by set_interface alias
        :param remote_object:
        :param remote_interface:
        :return:
        """
        return remote_interface
