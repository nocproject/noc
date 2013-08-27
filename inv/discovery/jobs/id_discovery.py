## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Id Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.inv.models.discoveryid import DiscoveryID
from noc.settings import config


class IDDiscoveryJob(MODiscoveryJob):
    name = "id_discovery"
    map_task = "get_discovery_id"

    ignored = not config.getboolean("id_discovery", "enabled")
    initial_submit_interval = config.getint("id_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("id_discovery",
        "initial_submit_concurrency")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        cm = result.get("chassis_mac")
        if cm:
            cm = ", ".join(
                "%s - %s" % (m["first_chassis_mac"], m["last_chassis_mac"])
                for m in cm
            )
        self.info("Identity found: Chassis MACs = %s, hostname = %s, router-id = %s" % (
            cm,
            result.get("hostname"),
            result.get("router_id")
        ))
        DiscoveryID.submit(object=object,
            chassis_mac=result.get("chassis_mac"),
            hostname=result.get("hostname"),
            router_id=result.get("router_id")
        )
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_id_discovery": True}

    def can_run(self):
        return (super(IDDiscoveryJob, self).can_run()
                and self.object.object_profile.enable_id_discovery)

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.id_discovery_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.id_discovery_min_interval
