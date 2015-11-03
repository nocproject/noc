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
from version import VersionCheck
from caps import CapsCheck
from interface import InterfaceCheck
from id import IDCheck


class BoxDiscoveryJob(MODiscoveryJob):
    name = "box"

    def handler(self, **kwargs):
        if self.object.object_profile.enable_box_discovery_version:
            VersionCheck(self).run()
        if self.object.object_profile.enable_box_discovery_caps:
            CapsCheck(self).run()
        if self.object.object_profile.enable_box_discovery_interface:
            InterfaceCheck(self).run()
        if self.object.object_profile.enable_box_discovery_id:
            IDCheck(self).run()

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_box_discovery
        )

    def get_interval(self):
        return self.object.object_profile.box_discovery_failed_interval

    def get_failed_interval(self):
        return self.object.object_profile.box_discovery_interval
