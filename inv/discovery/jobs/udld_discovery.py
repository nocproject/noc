## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UDLD Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config
from noc.inv.models.discoveryid import DiscoveryID


class UDLDLinkDiscoveryJob(LinkDiscoveryJob):
    """
    UDLD Link Discovery
    """
    name = "udld_discovery"
    map_task = "get_udld_neighbors"
    method = "udld"
    ignored = not config.getboolean("udld_discovery", "enabled")
    initial_submit_interval = config.getint("udld_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("udld_discovery",
        "initial_submit_concurrency")

    def process_result(self, object, result):
        self.n_cache = {}  # device_id -> object
        local_id = None  # Local IDs
        for n in result:
            local_id = n["local_device"]
            self.n_cache[local_id] = object
            remote_object = self.get_neighbor(n["remote_device"])
            if not remote_object:
                continue
            self.submit_candidate(n["local_interface"],
                remote_object,
                remote_object.profile.convert_interface_name(n["remote_interface"]))
        # Update UDLD id
        if local_id:
            self.update_udld_id(object, local_id)

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
        n = DiscoveryID.objects.filter(udld_id=device_id).first()
        if n:
            n = n.object
        self.n_cache[device_id] = n
        return n

    def update_udld_id(self, object, local_id):
        """
        Update UDLD id if necessary
        :param local_id:
        :return:
        """
        n = DiscoveryID.objects.filter(object=object.id).first()
        if n:
            # Found
            if n.udld_id != local_id:
                self.info("Setting local UDLD id to '%s'" % local_id)
                n.udld_id = local_id
                n.save()
        else:
            # Not Found
            self.info("Setting local UDLD id to '%s'" % local_id)
            DiscoveryID(
                object=object,
                udld_id=local_id
            ).save()
