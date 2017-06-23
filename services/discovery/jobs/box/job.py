#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Box Discovery Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random
# NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from suggestsnmp import SuggestSNMPCheck
from profile import ProfileCheck
from suggestcli import SuggestCLICheck
from version import VersionCheck
from caps import CapsCheck
from interface import InterfaceCheck
from id import IDCheck
from config import ConfigCheck
from asset import AssetCheck
from vlan import VLANCheck
from cdp import CDPCheck
from huawei_ndp import HuaweiNDPCheck
from oam import OAMCheck
from lldp import LLDPCheck
from lacp import LACPCheck
from stp import STPCheck
from nri import NRICheck
from sla import SLACheck
from cpe import CPECheck
from hk import HouseKeepingCheck
from noc.services.discovery.jobs.periodic.mac import MACCheck


class BoxDiscoveryJob(MODiscoveryJob):
    name = "box"
    umbrella_cls = "Discovery | Job | Box"

    TOPOLOGY_METHODS = [
        OAMCheck,
        LACPCheck,
        LLDPCheck,
        CDPCheck,
        HuaweiNDPCheck,
        STPCheck,
        NRICheck
    ]

    TOPOLOGY_NAMES = [m.name for m in TOPOLOGY_METHODS]

    def handler(self, **kwargs):
        if self.object.auth_profile and self.object.auth_profile.enable_suggest:
            SuggestSNMPCheck(self).run()
        if self.object.object_profile.enable_box_discovery_profile:
            ProfileCheck(self).run()
        if self.object.auth_profile and self.object.auth_profile.enable_suggest:
            SuggestCLICheck(self).run()
        if self.object.auth_profile and self.object.auth_profile.type == "S":
            self.logger.info(
                "Cannot choose valid credentials. Stopping"
            )
            return
        if self.allow_sessions():
            self.logger.debug("Using CLI sessions")
            with self.object.open_session():
                self.run_checks()
        else:
            self.run_checks()

    def run_checks(self):
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
        if self.object.object_profile.enable_box_discovery_nri:
            NRICheck(self).run()
        if self.object.object_profile.enable_box_discovery_cpe:
            CPECheck(self).run()
        if self.object.object_profile.enable_box_discovery_mac:
            MACCheck(self).run()
        # Topology discovery
        # Most preferable methods first
        for check in self.TOPOLOGY_METHODS:
            if getattr(self.object.object_profile,
                       "enable_box_discovery_%s" % check.name) and check.name != "nri":
                check(self).run()
        if self.object.object_profile.enable_box_discovery_sla:
            SLACheck(self).run()
        if self.object.object_profile.enable_box_discovery_hk:
            HouseKeepingCheck(self).run()

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_box_discovery
        )

    def get_interval(self):
        if self.object:
            return self.object.object_profile.box_discovery_interval
        else:
            # Dereference error
            return random.randint(270, 330)

    def get_failed_interval(self):
        return self.object.object_profile.box_discovery_failed_interval

    def is_preferable_method(self, m1, m2):
        """
        Returns True if m1 topology discovery method is
        preferable over m2
        """
        if m1 == m2:
            return True
        try:
            i1 = self.TOPOLOGY_NAMES.index(m1)
            i2 = self.TOPOLOGY_NAMES.index(m2)
        except ValueError:
            return False
        return i1 <= i2

    def can_update_alarms(self):
        return self.object.can_create_box_alarms()

    def get_fatal_alarm_weight(self):
        return self.object.object_profile.box_discovery_fatal_alarm_weight

    def get_alarm_weight(self):
        return self.object.object_profile.box_discovery_alarm_weight
