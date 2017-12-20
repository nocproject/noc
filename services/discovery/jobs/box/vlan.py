# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vlan check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.networksegment import NetworkSegment
from noc.vc.models.vlan import VLAN
from noc.core.perf import metrics


class VLANCheck(DiscoveryCheck):
    """
    VLAN discovery
    """
    name = "vlan"
    required_script = "get_vlans"
    # @todo: required_capabilities = ?
    # Fetch all segment VLANs if exceeded
    FULL_VLANS_THRESHOLD = 50

    def handler(self):
        self.logger.info("Checking VLANs")
        if not self.object.segment.profile.enable_vlan:
            self.logger.info(
                "VLAN discovery is disabled for segment '%s'. Skipping",
                self.object.segment.name
            )
            return
        # Get list of VLANs from equipment
        obbject_vlans = [
            (v["vlan_id"], v.get("name"))
            for v in self.object.scripts.get_vlans()
        ]
        if not obbject_vlans:
            self.logger.info("No any VLAN found. Skipping")
            return
        # Cache in case of large amount of vlans on equipment
        segment = NetworkSegment.get_border_segment(self.object.segment)
        if len(obbject_vlans) >= self.FULL_VLANS_THRESHOLD:
            metrics["vlan_segment_fetch"] += 1
            vlan_cache = dict(
                (v.vlan, v)
                for v in VLAN.objects.filter(segment=segment.id)
            )
        else:
            vlan_cache = {}
        # Refresh vlans
        vlans = [
            self.ensure_vlan(vlan_id, vlan_name, segment, vlan_cache)
            for vlan_id, vlan_name in obbject_vlans
        ]
        # Refresh discovery timestamps
        bulk = []
        for vlan in vlans:
            vlan.touch(bulk)
        if bulk:
            self.logger.info("Bulk update %d timestamps", len(bulk))
            VLAN._get_collection().bulk_write(bulk, ordered=True)
        # Send seen events
        for vlan in vlans:
            vlan.fire_event("seen")

    def ensure_vlan(self, vlan_id, vlan_name, segment, vlan_cache):
        """
        Refresh VLAN status in database, create when necessary
        :param vlan_id:
        :param vlan_name:
        :param segment:
        :param vlan_cache:
        :return:
        """
        if vlan_cache:
            # Get from cache
            metrics["vlan_cached_get"] += 1
            vlan = vlan_cache.get(vlan_id)
        else:
            # Get from database
            metrics["vlan_db_get"] += 1
            vlan = VLAN.objects.filter(segment=segment, vlan=vlan_id).first()
        # Create VLAN when neccessary
        if not vlan:
            self.logger.info("[%s] Creating VLAN %s(%s)",
                             segment.name, vlan_id, vlan_name)
            vlan = VLAN(
                name=vlan_name or self.get_default_vlan_name(vlan_id),
                profile=segment.profile.default_vlan_profile,
                vlan=vlan_id,
                segment=segment,
                description=self.get_default_vlan_description(vlan_id)
            )
            vlan.save()
            metrics["vlan_created"] += 1
        return vlan

    def get_default_vlan_name(self, vlan_id):
        """
        Generate VLAN name when not defined on equipment
        :param vlan_id:
        :return:
        """
        return "VLAN%s" % vlan_id

    def get_default_vlan_description(self, vlan_id):
        """
        Generate VLAN description
        :param vlan_id:
        :return:
        """
        return "Discovered at %s(%s)" % (self.object.name, self.object.address)
