#!./bin/python
# ---------------------------------------------------------------------
# Box Discovery Job
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import random

# NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from noc.core.span import Span
from noc.core.change.policy import change_tracker
from .resolver import ResolverCheck
from .version import VersionCheck
from .caps import CapsCheck
from .interface import InterfaceCheck
from .id import IDCheck
from .config import ConfigCheck
from .configvalidation import ConfigValidationCheck
from .asset import AssetCheck
from .vlan import VLANCheck
from .bgppeer import BGPPeerCheck
from .cdp import CDPCheck
from .huawei_ndp import HuaweiNDPCheck
from .oam import OAMCheck
from .lldp import LLDPCheck
from .lacp import LACPCheck
from .stp import STPCheck
from .udld import UDLDCheck
from .xmac import XMACCheck
from .nri_portmap import NRIPortmapperCheck
from .nri import NRICheck
from .nri_service import NRIServiceCheck
from .sla import SLACheck
from .cpe import CPECheck
from .bfd import BFDCheck
from .fdp import FDPCheck
from .rep import REPCheck
from .hk import HouseKeepingCheck
from .vpn import VPNCheck
from .prefix import PrefixCheck
from .address import AddressCheck
from .segmentation import SegmentationCheck
from .ifdesc import IfDescCheck
from .configparam import ConfigParamCheck
from ..periodic.diagnostic import DiagnosticCheck
from ..periodic.mac import MACCheck


class BoxDiscoveryJob(MODiscoveryJob):
    name = "box"
    umbrella_cls = "Discovery | Job | Box"

    # Store context
    context_version = 1

    TOPOLOGY_METHODS = {
        m.name: m
        for m in [
            OAMCheck,
            LACPCheck,
            UDLDCheck,
            LLDPCheck,
            BFDCheck,
            CDPCheck,
            FDPCheck,
            HuaweiNDPCheck,
            REPCheck,
            STPCheck,
            XMACCheck,
            IfDescCheck,
        ]
    }

    is_box = True

    default_contexts = ("counters", "metric_windows", "active_thresholds")

    def handler(self, **kwargs):
        with Span(sample=self.object.box_telemetry_sample), change_tracker.bulk_changes():
            has_cli = "C" in self.object.get_access_preference()
            ResolverCheck(self).run()
            DiagnosticCheck(self, run_order="S").run()
            # Run remaining checks
            if has_cli and self.allow_sessions():
                self.logger.debug("Using CLI sessions")
                with self.object.open_session():
                    self.run_checks()
            else:
                self.run_checks()

    def run_checks(self):
        if self.object.object_profile.enable_box_discovery_version:
            VersionCheck(self).run()
        if self.object.object_profile.enable_box_discovery_config:
            ConfigCheck(self).run()
        if self.object.object_profile.enable_box_discovery_caps:
            CapsCheck(self).run()
        if self.object.object_profile.enable_box_discovery_asset:
            AssetCheck(self).run()
        if self.object.object_profile.enable_box_discovery_interface:
            InterfaceCheck(self).run()
        if self.object.object_profile.enable_box_discovery_id:
            IDCheck(self).run()
        if self.object.object_profile.enable_box_discovery_config:
            ConfigValidationCheck(self).run()
        if VLANCheck.is_enabled_for_object(self.object):
            VLANCheck(self).run()
        if self.object.object_profile.enable_box_discovery_nri_portmap:
            NRIPortmapperCheck(self).run()
        if self.object.object_profile.enable_box_discovery_nri:
            NRICheck(self).run()
        if self.object.object_profile.enable_box_discovery_nri_service:
            NRIServiceCheck(self).run()
        if self.object.object_profile.enable_box_discovery_cpe:
            CPECheck(self).run()
        if VPNCheck.is_enabled_for_object(self.object):
            VPNCheck(self).run()
        if self.object.object_profile.enable_box_discovery_bgppeer:
            BGPPeerCheck(self).run()
        if PrefixCheck.is_enabled_for_object(self.object):
            PrefixCheck(self).run()
        if AddressCheck.is_enabled_for_object(self.object):
            AddressCheck(self).run()
        if (
            self.object.enable_autosegmentation
            or self.object.object_profile.enable_box_discovery_xmac
        ):
            MACCheck(self).run()
        if self.object.enable_autosegmentation:
            SegmentationCheck(self).run()
        # Topology discovery
        # Most preferable methods first
        for m in self.object.segment.profile.get_topology_methods():
            check = self.TOPOLOGY_METHODS.get(m)
            if not check:
                continue
            if getattr(self.object.object_profile, "enable_box_discovery_%s" % check.name):
                check(self).run()
        if self.object.object_profile.enable_box_discovery_sla:
            SLACheck(self).run()
        if self.object.object_profile.enable_box_discovery_hk:
            HouseKeepingCheck(self).run()
        if self.object.object_profile.enable_box_discovery_param_data:
            ConfigParamCheck(self).run()
        DiagnosticCheck(self, run_order="E").run()

    def get_running_policy(self):
        return self.object.get_effective_box_discovery_running_policy()

    def can_run(self):
        return super().can_run() and self.object.object_profile.enable_box_discovery

    def get_interval(self):
        if self.object:
            return self.object.object_profile.box_discovery_interval
        else:
            # Dereference error
            return random.randint(270, 330)

    def get_failed_interval(self):
        return self.object.object_profile.box_discovery_failed_interval

    def can_update_alarms(self):
        return self.object.can_create_box_alarms()

    def get_fatal_alarm_weight(self):
        return self.object.object_profile.box_discovery_fatal_alarm_weight

    def get_alarm_weight(self):
        return self.object.object_profile.box_discovery_alarm_weight

    def is_confdb_required(self):
        """
        Check if ConfDB is required by checks
        :return:
        """
        mo = self.object
        mop = self.object.object_profile
        if mop.enable_box_discovery_caps and mo.get_caps_discovery_policy() != "s":
            return True
        if mop.enable_box_discovery_interface and mo.get_interface_discovery_policy() != "s":
            return True
        if mop.vlan_vlandb_discovery != "D" and mo.get_vlan_discovery_policy() != "s":
            return True
        if (
            mop.enable_box_discovery_vpn_confdb
            or mop.enable_box_discovery_address_confdb
            or mop.enable_box_discovery_prefix_confdb
        ):
            return True
        if mop.enable_box_discovery_bgppeer:
            return True
        return False
