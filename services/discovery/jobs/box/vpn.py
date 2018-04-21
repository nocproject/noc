# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VPN discovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import namedtuple
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.ip.models.vrf import VRF
from noc.core.perf import metrics
from noc.core.handler import get_handler

DiscoveredVPN = namedtuple("DiscoveredVPN", [
    "type",
    "rd",
    "vpn_id",
    "name",
    "profile",
    "description",
    "source"
])

SRC_INTERFACE = "i"
SRC_MPLS = "m"
SRC_MANUAL = "M"

PREF_VALUE = {
    SRC_INTERFACE: 0,
    SRC_MPLS: 1,
    SRC_MANUAL: 2
}


class VPNCheck(DiscoveryCheck):
    name = "vpn"

    def handler(self):
        vpns = self.get_vpns()
        self.sync_vpns(vpns)

    def get_vpns(self):
        """
        Discover VPNs
        :return: dict of vpn_id => DiscoveredVPN
        """
        # vpn_id => DiscoveredVPNs
        vpns = {}
        # Apply interface prefixes
        if self.object.object_profile.enable_box_discovery_vpn_interface:
            vpns = self.apply_vpns(
                vpns,
                self.get_interface_vpns()
            )
        if self.object.object_profile.enable_box_discovery_vpn_mpls:
            vpns = self.apply_vpns(
                vpns,
                self.get_mpls_vpns()
            )

        return vpns

    def sync_vpns(self, vpns):
        """
        Apply VPNs to database.
        Temporary solution, applies only type == "VRF"
        :param vpns:
        :return:
        """
        # Get existing VRFs
        self.logger.debug("Getting VRFs to synchronize")
        vrfs = dict((vrf.vpn_id, vrf) for vrf in VRF.objects.filter(vpn_id__in=list(vpns)))
        #
        seen = set()
        # Apply changes
        for vpn_id in vpns:
            vpn = vpns[vpn_id]
            if vpn.type != "VRF":
                continue  # @todo: Only VRFs for now
            if vpn_id in vrfs:
                # Confirmed VPN, apply changes and touch
                self.apply_vpn_changes(vrfs[vpn_id], vpn)
                seen.add(vpn_id)
        # Create new VPNs
        for vpn_id in set(vpns) - seen:
            vpn = vpns[vpn_id]
            if vpn.type != "VRF":
                continue  # @todo: Only VRFs for now
            self.create_vpn(vpn)

    @staticmethod
    def apply_vpns(vpns, discovered_vpns):
        """
        Apply list of discovered vpns to vpn dict
        :param vpns: dict of vpn_id => DiscoveredVPN
        :param discovered_vpns: List of [DiscoveredVPN]
        :returns: Resulted vpns
        """
        for vpn in discovered_vpns:
            if not vpn.vpn_id:
                metrics["vpn_wo_vpn_id"] += 1
                continue
            old = vpns.get(vpn.vpn_id)
            if old:
                if VPNCheck.is_preferred(old.source, vpn.source):
                    # New prefix is preferable, replace
                    vpns[vpn.vpn_id] = vpn
            else:
                # Not seen yet
                vpns[vpn.vpn_id] = vpn
        return vpns

    def is_enabled(self):
        enabled = super(VPNCheck, self).is_enabled()
        if not enabled:
            return False
        return self.is_enabled_for_object(self.object)

    def get_interface_vpns(self):
        """
        Get VPNs from interface discovery artifact
        :return: List of DiscoveredVPN
        """
        self.logger.debug("Getting interface VPNs")
        if not self.object.object_profile.vpn_profile_interface:
            self.logger.info("Default interface VPN profile is not set. Skipping interface VPN discovery")
            return []
        vpns = self.get_artefact("interface_vpn")
        if not vpns:
            self.logger.info("No interface_vpn artefact, skipping interface prefixes")
            return []
        return [
            DiscoveredVPN(
                rd=p["rd"],
                vpn_id=p.get("vpn_id"),
                name=p["name"],
                type=p["type"],
                profile=self.object.object_profile.vpn_profile_interface,
                source=SRC_INTERFACE,
                description=None
            )
            for p in vpns.values()
        ]

    def get_mpls_vpns(self):
        """
        Get VPNs from get_mpls_vpn script
        :return: List of DiscoveredVPN
        """
        if not self.object.object_profile.vpn_profile_mpls:
            self.logger.info("Default MPLS VPN profile is not set. Skipping MPLS VPN discovery")
            return []
        # @todo: Check VPN capability
        if "get_mpls_vpn" not in self.object.scripts:
            self.logger.info("No get_mpls_vpn script, skipping MPLS VPN discovery")
            return []
        self.logger.debug("Getting MPLS VPNS")
        vpns = self.object.scripts.get_mpls_vpn()
        r = [
            DiscoveredVPN(
                rd=vpn["rd"],
                vpn_id=vpn["vpn_id"],
                name=vpn["name"],
                type=vpn["type"],
                profile=self.object.object_profile.vpn_profile_mpls,
                description=vpn.get("description"),
                source=SRC_MPLS
            ) for vpn in vpns if vpn.get("vpn_id")
        ]
        return r

    @staticmethod
    def is_preferred(old_method, new_method):
        """
        Check which method is preferable

        Preference order: interface, management, neighbor
        :param old_method:
        :param new_method:
        :return:
        """
        return PREF_VALUE[old_method] <= PREF_VALUE[new_method]

    def create_vpn(self, vpn):
        """
        Create new vpn
        :param vpn: DiscoveredVPN instance
        :return:
        """
        if not self.has_vpn_permission(vpn):
            self.logger.debug(
                "Do not creating rd=%s vpn_id=%s name=%s Disabled by policy",
                vpn.rd, vpn.vpn_id, vpn.name
            )
            metrics["vpn_creation_denied"] += 1
            return
        name = self.get_vpn_name(vpn)
        # Check for naming clash
        if VRF.objects.filter(name=name).exists():
            # Naming clash
            old_name = name
            name = self.get_unique_vpn_name(vpn)
            self.logger.info(
                "Name '%s' is already exists with other vpn_id. Rename to '%s'",
                old_name, name
            )
            metrics["vpn_name_clash"] += 1
        #
        p = VRF(
            name=name,
            rd=vpn.rd,
            vpn_id=vpn.vpn_id,
            profile=vpn.profile,
            source=vpn.source
        )
        self.logger.info(
            "Creating vpn %s: name=%s rd=%s profile=%s source=%s",
            p.vpn_id, p.name, p.rd, p.profile.name, p.source
        )
        p.save()
        p.fire_event("seen")
        metrics["vpn_created"] += 1

    def apply_vpn_changes(self, vpn, discovered_vpn):
        """
        Apply vpn changes and send signals
        :param vpn: VRF instance
        :param discovered_vpn: DiscoveredVPN instance
        :return:
        """
        if self.is_preferred(vpn.source, discovered_vpn.source):
            changes = []
            if vpn.source != discovered_vpn.source:
                changes += ["source: %s -> %s" % (vpn.source, discovered_vpn.source)]
                vpn.source = discovered_vpn.source
            if (
                discovered_vpn.name and
                discovered_vpn.name != vpn.name and
                self.get_unique_vpn_name(discovered_vpn) != vpn.name
            ):
                changes += ["name: %s -> %s" % (vpn.name, discovered_vpn.name)]
                vpn.name = discovered_vpn.name
            if changes:
                self.logger.info(
                    "Changing %s: %s",
                    vpn.vpn_id,
                    ", ".join(changes)
                )
                vpn.save()
                metrics["vpn_updated"] += 1
        else:
            self.logger.debug(
                "Do not updating vpn_id=%s. Source level too low",
                discovered_vpn.vpn_id
            )
            metrics["vpn_update_denied"] += 1
        vpn.fire_event("seen")

    def has_vpn_permission(self, vpn):
        """
        Check discovery has permission to manipulate vpn
        :param vpn: DiscoveredVPN instance
        :return:
        """
        # @todo: Implement properly
        return True

    def get_vpn_name(self, vpn):
        """
        Render address name
        :param prefix: DiscoveredVPN instance
        :return: Rendered name
        """
        if vpn.profile.name_template:
            name = vpn.profile.name_template.render_subject(
                **self.get_template_context(vpn)
            )
            return self.strip(name)
        return vpn.name or vpn.vpn_id or vpn.rd

    @staticmethod
    def strip(s):
        return s.replace("\n", "").strip()

    def get_template_context(self, vpn):
        return {
            "vpn": vpn,
            "get_handler": get_handler,
            "object": self.object
        }

    @staticmethod
    def is_enabled_for_object(object):
        return (
            object.object_profile.enable_box_discovery_vpn_interface or
            object.object_profile.enable_box_discovery_vpn_mpls
        )

    def get_unique_vpn_name(self, vpn):
        """
        Generate unique VPN name by adding vpn_id or rd
        :param vpn: DiscoveredVPN
        :return: unique name
        """
        return "%s (%s)" % (
            self.get_vpn_name(vpn),
            vpn.vpn_id or vpn.rd
        )
