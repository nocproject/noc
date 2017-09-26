#!./bin/python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Box Discovery Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import random
# NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from .suggestsnmp import SuggestSNMPCheck
from .profile import ProfileCheck
from .suggestcli import SuggestCLICheck
from .version import VersionCheck
from .caps import CapsCheck
from .interface import InterfaceCheck
from .id import IDCheck
from .config import ConfigCheck
from .asset import AssetCheck
from .vlan import VLANCheck
from .cdp import CDPCheck
from .huawei_ndp import HuaweiNDPCheck
from .oam import OAMCheck
from .lldp import LLDPCheck
from .lacp import LACPCheck
from .stp import STPCheck
from .udld import UDLDCheck
from .nri import NRICheck
from .sla import SLACheck
from .cpe import CPECheck
from .hk import HouseKeepingCheck
from noc.services.discovery.jobs.periodic.mac import MACCheck
from noc.services.discovery.jobs.periodic.metrics import MetricsCheck
from noc.core.span import Span


class BoxDiscoveryJob(MODiscoveryJob):
    name = "box"
    umbrella_cls = "Discovery | Job | Box"

    # Store context
    context_version = 1

    TOPOLOGY_METHODS = dict((m.name, m) for m in [
        OAMCheck,
        LACPCheck,
        UDLDCheck,
        LLDPCheck,
        CDPCheck,
        HuaweiNDPCheck,
        STPCheck,
        NRICheck
    ])

    def handler(self, **kwargs):
        with Span(sample=self.object.box_telemetry_sample):
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
            # Build topology methods
            self.topology_methods = []
            for ms in self.object.segment.profile.topology_methods:
                if ms.method not in self.TOPOLOGY_METHODS or not ms.is_active:
                    continue
                if ms.method in ("custom", "handler"):
                    # @todo: Implement
                    continue
                self.topology_methods += [self.TOPOLOGY_METHODS[ms.method]]
            self.topology_names = [m.name for m in self.topology_methods]
            #
            self.reboot_detected = False
            # Run remaining checks
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
        for check in self.topology_methods:
            if getattr(self.object.object_profile,
                       "enable_box_discovery_%s" % check.name) and check.name != "nri":
                check(self).run()
        if self.object.object_profile.enable_box_discovery_sla:
            SLACheck(self).run()
        if self.object.object_profile.enable_box_discovery_metrics:
            MetricsCheck(self).run()
        if self.object.object_profile.enable_box_discovery_hk:
            HouseKeepingCheck(self).run()

    def can_run(self):
        return (super(BoxDiscoveryJob, self).can_run() and
                self.object.object_profile.enable_box_discovery)

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
            i1 = self.topology_names.index(m1)
            i2 = self.topology_names.index(m2)
        except ValueError:
            return False
        return i1 <= i2

    def can_update_alarms(self):
        return self.object.can_create_box_alarms()

    def get_fatal_alarm_weight(self):
        return self.object.object_profile.box_discovery_fatal_alarm_weight

    def get_alarm_weight(self):
        return self.object.object_profile.box_discovery_alarm_weight

    def init_context(self):
        if "counters" not in self.context:
            self.context["counters"] = {}
        if "metrics_window" not in self.context:
            self.context["metric_windows"] = {}
