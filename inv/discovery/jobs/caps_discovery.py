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
    name = "caps_discovery"
    map_task = "get_capabilities"

    ignored = not config.getboolean("caps_discovery", "enabled")
    to_save = config.getboolean("caps_discovery", "save")

    def handler(self, object, result):
        self.logger.info("Set capabilities: %s", result)
        self.object.update_caps(result)
        return True

    def can_run(self):
        return (super(CapsDiscoveryJob, self).can_run()
                and self.object.object_profile.enable_caps_discovery)

    def get_failed_interval(self):
        return self.object.object_profile.version_inventory_min_interval
