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
from profile import ProfileCheck
from version import VersionCheck
from caps import CapsCheck
from interface import InterfaceCheck
from id import IDCheck
from config import ConfigCheck
from asset import AssetCheck
from vlan import VLANCheck
from cdp import CDPCheck
from oam import OAMCheck
from lldp import LLDPCheck


class BoxDiscoveryJob(MODiscoveryJob):
    name = "box"

    TOPOLOGY_METHODS = [
        OAMCheck,
        LLDPCheck,
        CDPCheck
    ]

    TOPOLOGY_NAMES = [m.name for m in TOPOLOGY_METHODS]

    def handler(self, **kwargs):
        if self.object.object_profile.enable_box_discovery_profile:
            ProfileCheck(self).run()
        if self.object.object_profile.enable_box_discovery_version:
            VersionCheck(self).run()
        if self.object.object_profile.enable_box_discovery_caps:
            CapsCheck(self).run()
        if self.object.object_profile.enable_box_discovery_interface:
            InterfaceCheck(self).run()
        if self.object.object_profile.enable_box_discovery_id:
            IDCheck(self).run()
        if self.object.object_profile.enable_box_discovery_config:
            ConfigCheck(self).run()
        if self.object.object_profile.enable_box_discovery_asset:
            AssetCheck(self).run()
        if self.object.object_profile.enable_box_discovery_vlan:
            VLANCheck(self).run()
        # Topology discovery
        # Most preferable methods first
        for check in self.TOPOLOGY_METHODS:
            if getattr(self.object.object_profile,
                       "enable_box_discovery_%s" % check.name):
                check(self).run()

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_box_discovery
        )

    def get_interval(self):
        return self.object.object_profile.box_discovery_failed_interval

    def get_failed_interval(self):
        return self.object.object_profile.box_discovery_interval

    def is_preferable_method(self, m1, m2):
        """
        Returns True if m1 topology discovery method is
        preferable over m2
        """
        if m1 == m2:
            return True
        try:
            i1 = self.TOPOLOGY_NAMES.index(m1)
        except ValueError:
            return False
        try:
            i2 = self.TOPOLOGY_NAMES.index(m2)
        except ValueError:
            return True
        return i1 <= i2
