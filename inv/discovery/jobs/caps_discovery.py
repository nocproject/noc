## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Capability discovery job
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.settings import config
from base import MODiscoveryJob


class CapsDiscoveryJob(MODiscoveryJob):
    name = "caps_disovery"
    map_task = "get_capabilities"

    ignored = not config.getboolean("caps_discovery", "enabled")
    initial_submit_interval = config.getint("caps_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("caps_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("caps_discovery", "save")

    def handler(self, object, result):
        self.logger.info("Set capabilities: %s", result)
        self.object.update_caps(result)
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_caps_discovery": True}

    def can_run(self):
        return (super(CapsDiscoveryJob, self).can_run()
                and self.object.object_profile.enable_caps_discovery)

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.version_inventory_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.version_inventory_min_interval
