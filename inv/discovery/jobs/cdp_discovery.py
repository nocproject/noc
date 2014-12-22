## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CDP Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config
from noc.inv.models.discoveryid import DiscoveryID


class CDPLinkDiscoveryJob(LinkDiscoveryJob):
    """
    CDP Link Discovery
    """
    name = "cdp_discovery"
    map_task = "get_cdp_neighbors"
    method = "cdp"
    ignored = not config.getboolean("cdp_discovery", "enabled")

    def process_result(self, object, result):
        self.n_cache = {}  # device_id -> object
        for n in result["neighbors"]:
            remote_object = self.get_neighbor(n["device_id"])
            if not remote_object:
                continue
            remote_port = remote_object.profile.convert_interface_name(
                n["remote_interface"])
            self.submit_candidate(
                n["local_interface"], remote_object, remote_port)

    def get_neighbor(self, device_id):
        """
        Find neighbor by chassis id and chassis subtype
        :param device_id:
        :return:
        """
        # Get cached
        n = self.n_cache.get(device_id)
        if n:
            return n
        n = DiscoveryID.objects.filter(hostname=device_id).first()
        if n:
            n = n.object
        elif "." not in device_id:
            # Sometimes, domain part is truncated.
            # Try to resolve anyway
            m = list(DiscoveryID.objects.filter(
                hostname__startswith=device_id + "."))
            if len(m) == 1:
                n = m[0].object  # Exact match
        self.n_cache[device_id] = n
        return n
