#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Box Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob


class BoxDiscoveryJob(MODiscoveryJob):
    name = "box"

    def handler(self, **kwargs):
        if self.object.object_profile.enable_box_discovery_version:
            self.logger.info("Checking version")
            self.check_version()

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_box_discovery
        )

    def get_interval(self):
        return self.object.object_profile.box_discovery_failed_interval

    def get_failed_interval(self):
        return self.object.object_profile.box_discovery_interval

    def check_version(self):
        """
        Version discovery
        """
        result = self.object.scripts.get_version()
        r = {}
        for k in result:
            v = result[k]
            if k == "attributes":
                for kk in v:
                    r[kk] = v[kk]
            else:
                r[k] = v
        for k in r:
            v = r[k]
            ov = self.object.get_attr(k)
            if ov != v:
                self.object.set_attr(k, v)
                self.logger.info("[version] %s: %s -> %s", k, ov, v)
